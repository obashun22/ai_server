# AI Response Server

Claude AIを使用したTCPベースのHTTPサーバー

## 概要

AI Response Serverは、従来のWebフレームワークを使わず、TCPソケットで直接HTTPリクエストを処理するシンプルなHTTPサーバーです。Claude AI (Sonnet 4.5) がリクエスト内容を解釈し、適切なHTTPレスポンスを動的に生成します。

## 特徴

- 🚀 **フレームワークレス** - FastAPI等を使わない生のTCP実装
- 🤖 **AI駆動** - Claude AIがHTTPリクエストを解釈してレスポンスを生成
- 📝 **標準準拠ログ** - Apache/Nginx風のアクセスログフォーマット
- 🔧 **シンプル** - わずか161行のPythonコード
- ⚡ **最小限の依存** - `anthropic`と`python-dotenv`のみ

## 必要要件

- Python 3.10以上
- Claude API キー（Anthropic）

## インストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd ai_server

# 仮想環境を作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt

# 環境変数を設定
cp .env.example .env
# .envファイルを編集してANTHROPIC_API_KEYを設定
```

## 使い方

### サーバー起動

```bash
python main.py
```

デフォルトで`0.0.0.0:8000`でリッスンします。

### 環境変数

`.env`ファイルで設定可能：

```env
ANTHROPIC_API_KEY=your_api_key_here
HOST=0.0.0.0
PORT=8000
```

### リクエスト例

```bash
# GETリクエスト
curl http://localhost:8000/

# POSTリクエスト
curl -X POST http://localhost:8000/api/data \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

### ログ出力例

```
2025-11-03 01:44:06 - INFO - Server started on 0.0.0.0:8000
2025-11-03 01:44:07 - INFO - 127.0.0.1 - - [02/Nov/2025:16:44:07 +0000] "GET /hello HTTP/1.1" - - "-" "-" - Request received
2025-11-03 01:44:10 - INFO - 127.0.0.1 - - [02/Nov/2025:16:44:10 +0000] "GET /hello HTTP/1.1" 200 13 "-" "-" 2.819s
```

## 技術スタック

- **Python** 3.10+
- **Claude AI** Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
- **anthropic** 0.72.0 - Claude API クライアント
- **python-dotenv** 1.0.0 - 環境変数管理

## プロジェクト構成

```
ai_server/
├── main.py              # メインプログラム (161行)
├── requirements.txt     # 依存パッケージ
├── .env.example         # 環境変数テンプレート
├── .gitignore          # Git除外設定
└── README.md           # このファイル
```

## アーキテクチャ

```
クライアント
    ↓ HTTPリクエスト
TCPサーバー (main.py)
    ↓ リクエスト解析
Claude AI (Sonnet 4.5)
    ↓ レスポンス生成
TCPサーバー
    ↓ HTTPレスポンス
クライアント
```

### 主要関数

| 関数 | 説明 |
|-----|------|
| `start_server()` | TCPサーバーを起動 |
| `handle_client()` | クライアント接続を処理 |
| `process_with_ai()` | Claude AIでHTTPリクエストを処理 |
| `parse_request_line()` | HTTPリクエストラインを解析 |
| `build_error_response()` | 500エラーレスポンスを構築 |

## 制約事項

- **同時接続**: 1接続のみ（同期処理）
- **リクエストサイズ**: 最大4096バイト
- **認証**: なし
- **HTTPS**: 非対応

## 開発

### コードスタイル

- コメント: 日本語
- Docstring: 日本語
- 命名規則: snake_case

### Git管理

```bash
# 変更をコミット
git add .
git commit -m "説明"

# ログ確認
git log --oneline
```

## ライセンス

MIT License

## 作者

Claude Code + Human
