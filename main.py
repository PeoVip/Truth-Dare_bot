import discord
from discord.ext import commands
import random
import asyncio
import json
import datetime

# Thay thế YOUR_TOKEN bằng token bot Discord của bạn
TOKEN = 'YOUR_TOKEN'

# Tiền tố lệnh
PREFIX = '!'

# Danh sách vai trò
ROLES = [
    "Bác sĩ", "Bảo vệ", "Người canh gác", "Quản Ngục", "Kỹ nữ", "Thầy Bói",
    "Thầy Đồng", "Hoa Bé Con", "Cậu Bé Miệng Bự", "Bán Sói", "Sói trẻ",
    "Sói Hắc Ám", "Sói Hộ Vệ", "Sói Tiên Tri", "Sói đầu đàn", "Thằng Ngố",
    "Thợ Săn Người", "Tin tặc", "Kẻ Phóng Hoả"
]

# Danh sách người chơi
players = {}

# Trạng thái trò chơi
game_started = False
night_time = False
votes = {}
protected = {} # Lưu trữ người được bảo vệ
jailed = {} # Lưu trữ người bị giam
arsoned = [] # Lưu trữ người chơi bị tẩm xăng
target_player = {} # Lưu trữ mục tiêu của thợ săn người
revealed_roles = {} # lưu trữ vai trò đã lộ của người chơi

# Tải lịch sử chơi từ file JSON (nếu có)
try:
    with open('history.json', 'r') as f:
        history = json.load(f)
except FileNotFoundError:
    history = {}

bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'{bot.user.name} đã sẵn sàng!')

@bot.command(name='start', help='Bắt đầu trò chơi Ma Sói.')
async def start(ctx, *player_mentions):
    global game_started, players, night_time, votes, protected, jailed, arsoned, target_player, revealed_roles

    if game_started:
        await ctx.send("Trò chơi đã bắt đầu rồi!")
        return

    if len(player_mentions) != 16:
        await ctx.send("Cần 16 người chơi để bắt đầu trò chơi.")
        return

    players = {}
    available_roles = ROLES[:]

    for mention in player_mentions:
        player = ctx.guild.get_member(int(mention[3:-1]))
        if player:
            role = random.choice(available_roles)
            players[player.id] = {"role": role, "alive": True}
            available_roles.remove(role)
        else:
            await ctx.send(f"Không tìm thấy người chơi {mention}.")
            return

    game_started = True
    night_time = True
    votes = {}
    protected = {}
    jailed = {}
    arsoned = []
    target_player = {}
    revealed_roles = {}
    
    #random target cho thợ săn người
    target_player[ctx.author.id] = random.choice(list(players.keys()))

    await ctx.send("Trò chơi Ma Sói đã bắt đầu! Đêm đầu tiên đã đến.")

    for player_id, player_info in players.items():
        player = bot.get_user(player_id)
        await player.send(f"Vai trò của bạn là: {player_info['role']}")
        if player_info['role'] == "Thợ Săn Người":
            await player.send(f"Mục tiêu của bạn là: {bot.get_user(target_player[ctx.author.id]).name}")

    await night_phase(ctx)

# Thêm các lệnh cho từng vai trò (Bác sĩ, Bảo vệ, Người canh gác, v.v.)
# ... (Thêm các lệnh cho từng vai trò) ...

@bot.command(name='vote', help='Bầu chọn người chơi bị nghi ngờ.')
async def vote(ctx, player_mention):
    global votes

    if not game_started or night_time:
        await ctx.send("Lệnh này chỉ dùng vào ban ngày!")
        return

    target_player = ctx.guild.get_member(int(player_mention[3:-1]))
    if target_player and target_player.id in players and players[target_player.id]["alive"]:
        if ctx.author.id not in votes:
            votes[ctx.author.id] = target_player.id
            await ctx.send(f"{ctx.author.name} đã bầu chọn {target_player.name}!")
        else:
            await ctx.send("Bạn đã bầu chọn rồi!")
    else:
        await ctx.send("Người chơi không hợp lệ hoặc đã chết!")

@bot.command(name='end', help='Kết thúc trò chơi.')
async def end(ctx):
    global game_started, players

    if not game_started:
        await ctx.send("Trò chơi chưa bắt đầu!")
        return

    game_started = False
    players = {}
    await ctx.send("Trò chơi đã kết thúc.")

async def night_phase(ctx):
    global night_time

    await asyncio.sleep(60)  # Đêm kéo dài 60 giây
    night_time = False
    await ctx.send("Bình minh đã đến!")
    await day_phase(ctx)

async def day_phase(ctx):
    global night_time, votes

    await asyncio.sleep(60)  # Ngày kéo dài 60 giây
    night_time = True
    await ctx.send("Đêm đã đến!")

    # Xử lý bầu chọn
    if votes:
        target = max(set(votes.values()), key=list(votes.values()).count)
        players[target]["alive"] = False
        await ctx.send(f"{bot.get_user(target).name} đã bị dân làng treo cổ!")
        votes = {}

    await night_phase(ctx)

bot.run(TOKEN)
