# Discord タスク管理Bot

Discordサーバー上でメンバーのタスクを管理し、期限前に自動でリマインドを送るBotです。

## 機能

- スラッシュコマンドでタスクの追加・一覧・完了ができる
- タスクはJSONファイルに保存されるため、Bot再起動後も消えない
- 毎日0時に期限3日前・1日前のタスクを自動通知

## 使用技術

- Python 3.x
- [discord.py](https://discordpy.readthedocs.io/) v2.x（スラッシュコマンド対応）
- python-dotenv（環境変数管理）

## コマンド一覧

| コマンド | 説明 |
|---|---|
| `/task_add user content deadline` | タスクを追加する（deadline形式: `YYYY-MM-DD HH:MM`） |
| `/task_list [user]` | タスク一覧を期限順に表示（userを指定すると絞り込み） |
| `/task_done task_id` | 指定IDのタスクを完了・削除する |

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/your-username/discord-bot.git
cd discord-bot
```

### 2. 依存ライブラリをインストール

```bash
pip install -r requirements.txt
```

### 3. `.env` ファイルを作成

```
DISCORD_TOKEN=your_bot_token_here
```

### 4. 通知チャンネルIDを設定

`bot.py` の `NOTIFY_CHANNEL_ID` を通知先チャンネルのIDに変更してください。

### 5. Botを起動

```bash
python bot.py
```
