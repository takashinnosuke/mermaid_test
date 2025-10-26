# Diagram Structure Reviewer

FastAPIベースのローカルWebアプリです。画像や図形からLLMで抽出した構造をMermaidとJSONでレビュー・編集できます。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env .env.local  # APIキー設定ファイルのサンプル
```

`.env.local` に `OPENAI_API_KEY` や `GEMINI_API_KEY` を設定してください。環境変数として読み込まれます。

## 起動

```bash
uvicorn app.main:app --reload
```

ブラウザで `http://localhost:8000` にアクセスします。

## 主なエンドポイント

| メソッド | パス | 説明 |
| --- | --- | --- |
| `POST` | `/upload` | 図や画像ファイルをアップロードし、一意のIDを取得します |
| `POST` | `/convert` | Gemini/ChatGPT APIを呼び出して構造JSONを生成します |
| `POST` | `/generate_mermaid` | JSONからMermaidコードを生成します |
| `GET` | `/review/{id}` | MermaidとJSON編集を含むレビュー画面を表示します |
| `PUT` | `/update_node` | 特定ノードのラベルやconfidenceを更新します |
| `PUT` | `/update_edge` | エッジ情報を更新します |
| `PUT` | `/update_json` | JSONエディタの内容を保存します |
| `GET` | `/diff/{id}` | DeepDiffによる差分を返します |
| `POST` | `/approve/{id}` | レビュー済みとしてバージョン保存します |

## フロントエンド機能

* MermaidプレビューとMonaco EditorによるJSON編集を同一画面に配置
* confidenceが低いノードのみをリスト化してレビューしやすく
* JSON更新時にMermaidを再描画し、差分タブにDeepDiff結果を表示
* 承認時に `data/versions/` にスナップショットを保存

## 備考

外部API呼び出しはダミー実装を含み、APIキーが設定されていない場合はサンプルJSONを返します。実際にGeminiやChatGPTを利用する際は、`app/routers/convert.py` 内の `_call_structure_api` を適宜修正してください。
