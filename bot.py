import discord
from discord import app_commands
from datetime import datetime, timedelta
import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        self.loop.create_task(daily_reminder())

    async def on_ready(self):
        print(f"ログイン成功: {self.user}")

client = MyClient()
tree = client.tree

NOTIFY_CHANNEL_ID = 1484197953668386967  # ←後で説明
TASKS_FILE = "tasks.json"


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks():
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


tasks = load_tasks()


def get_next_id():
    return max((t["id"] for t in tasks if "id" in t), default=-1) + 1


# タスク追加
@tree.command(name="task_add", description="タスクを追加")
async def task_add(interaction: discord.Interaction, user: discord.User, content: str, deadline: str):
    try:
        datetime.strptime(deadline, "%Y-%m-%d %H:%M")
    except ValueError:
        await interaction.response.send_message("期限の形式が違うで！`YYYY-MM-DD HH:MM` で入力してな（例: `2026-05-15 17:00`）")
        return

    task_id = get_next_id()
    tasks.append({
        "id": task_id,
        "user_id": user.id,
        "user_mention": user.mention,
        "content": content,
        "deadline": deadline
    })
    save_tasks()

    await interaction.response.send_message(
        f"[{task_id}] タスク追加したで！ {user.mention} - {content}（期限: {deadline}）"
    )

# タスク一覧
@tree.command(name="task_list", description="タスク一覧を表示")
async def task_list(interaction: discord.Interaction, user: discord.User = None):
    if not tasks:
        await interaction.response.send_message("タスクはまだないで！")
        return

    filtered = [t for t in tasks if (user is None or t["user_id"] == user.id)]

    if not filtered:
        await interaction.response.send_message("該当タスクなし！")
        return

    # 期限でソート
    filtered.sort(key=lambda t: datetime.strptime(t["deadline"], "%Y-%m-%d %H:%M"))

    message = ""
    for t in filtered:
        message += f"[{t['id']}] {t['user_mention']} | {t['content']} | 期限: {t['deadline']}\n"

    await interaction.response.send_message(message)

# タスク完了
@tree.command(name="task_done", description="タスクを完了")
async def task_done(interaction: discord.Interaction, task_id: int):
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(i)
            save_tasks()
            await interaction.response.send_message(f"完了！🎉 {t['content']}")
            return

    await interaction.response.send_message("そのIDのタスクは見つからへんで！")

# 🔔 毎日0時にリマインド
async def daily_reminder():
    await client.wait_until_ready()

    while True:
        now = datetime.now()
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        wait_seconds = (next_midnight - now).total_seconds()

        await asyncio.sleep(wait_seconds)

        channel = client.get_channel(NOTIFY_CHANNEL_ID)
        if channel is None:
            continue

        now = datetime.now()

        msg_3days = "📅【3日前リマインド】\n"
        msg_1day = "⏰【1日前リマインド】\n"

        has_3 = False
        has_1 = False

        for i, t in enumerate(tasks):
            try:
                deadline = datetime.strptime(t["deadline"], "%Y-%m-%d %H:%M")
                diff = (deadline - now).total_seconds()

                # 3日前
                if 2*86400 < diff <= 3*86400:
                    msg_3days += f"[{i}] {t['user_mention']} {t['content']}（{t['deadline']}）\n"
                    has_3 = True

                # 1日前
                if 0 < diff <= 86400:
                    msg_1day += f"[{i}] {t['user_mention']} {t['content']}（{t['deadline']}）\n"
                    has_1 = True

            except Exception as e:
                print(f"[daily_reminder] タスク{i}の処理中にエラー: {e}")

        if has_3:
            await channel.send(msg_3days)

        if has_1:
            await channel.send(msg_1day)

client.run(os.getenv("DISCORD_TOKEN"))
