(function () {
  const preview = document.getElementById("mermaid-preview");
  const diffOutput = document.getElementById("diff-output");
  const saveButton = document.getElementById("save-json");
  const regenerateButton = document.getElementById("regenerate-mermaid");
  const approveButton = document.getElementById("approve");
  const refreshDiffButton = document.getElementById("refresh-diff");

  let editorInstance;

  function renderMermaid(code) {
    if (!preview) return;
    preview.innerHTML = "";
    const insert = document.createElement("div");
    insert.className = "mermaid";
    insert.textContent = code;
    preview.appendChild(insert);
    mermaid.run({ nodes: [insert] });
  }

  function fetchDiff() {
    fetch(`/diff/${diagramId}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.message) {
          diffOutput.textContent = data.message;
        } else {
          diffOutput.textContent = JSON.stringify(data.diff, null, 2);
        }
      })
      .catch((err) => {
        diffOutput.textContent = `差分取得に失敗しました: ${err}`;
      });
  }

  function saveJson() {
    try {
      const content = editorInstance.getValue();
      const parsed = JSON.parse(content);
      fetch("/update_json", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ diagram_id: diagramId, payload: parsed }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.status === "ok") {
            renderMermaid(data.mermaid);
            fetchDiff();
          }
        })
        .catch((err) => console.error("Save failed", err));
    } catch (err) {
      alert("JSONのパースに失敗しました: " + err);
    }
  }

  function regenerateMermaid() {
    fetch("/generate_mermaid", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ diagram_id: diagramId }),
    })
      .then((res) => res.json())
      .then((data) => {
        renderMermaid(data.mermaid);
      })
      .catch((err) => console.error(err));
  }

  function approveDiagram() {
    fetch(`/approve/${diagramId}`, { method: "POST" })
      .then((res) => res.json())
      .then((data) => {
        alert(`承認しました: ${data.version}`);
        fetchDiff();
      })
      .catch((err) => alert(`承認に失敗しました: ${err}`));
  }

  if (saveButton) saveButton.addEventListener("click", saveJson);
  if (regenerateButton) regenerateButton.addEventListener("click", regenerateMermaid);
  if (approveButton) approveButton.addEventListener("click", approveDiagram);
  if (refreshDiffButton) refreshDiffButton.addEventListener("click", fetchDiff);

  require.config({ paths: { vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs" } });
  const proxy = URL.createObjectURL(
    new Blob(
      [
        `self.MonacoEnvironment = { baseUrl: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/' };
importScripts('https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs/base/worker/workerMain.js');`,
      ],
      { type: "text/javascript" }
    )
  );
  window.MonacoEnvironment = { getWorkerUrl: () => proxy };

  require(["vs/editor/editor.main"], function () {
    editorInstance = monaco.editor.create(document.getElementById("editor"), {
      value: initialJson,
      language: "json",
      theme: "vs-dark",
      automaticLayout: true,
    });
    renderMermaid(initialMermaid);
  });

  fetchDiff();
})();
