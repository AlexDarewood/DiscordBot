#Модули
import discord
import youtube_dl
import shutil
import os
import random
import json
import requests
from os import system
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import Bot
from booruComm import booruComm
from gelbooruCaller import gelbooruCaller
from UserCollection import UserCollection
from UserStatTracker import UserStatTracker
from auditor import Auditor
from UserLimiter import UserLimiter
from booruLib import booruLib
from filter import Filter
from clientConnections import ClientConnections

client = commands.Bot(command_prefix='ns!')
auditor = Auditor("audit.txt")
auditor.generateAuditLog()
auditLines = auditor.getInitialAuditLog()
users = UserCollection(auditLines)
userStats = UserStatTracker(users.getUsers(), auditLines)
gelbooruLimiter = UserLimiter()
ChannelFilter = Filter()
ClientConnector = ClientConnections()
ROLE = "Space🔮"
try:
    apiTokenFile = open('gelApiKey.config','r')
    apiToken = apiTokenFile.readline()
    apiTokenFile.close()
except OSError:
    print("No gelApiKey.config file found for a gelbooru api key, no api key will be used and you will not be able to access blacklisted content.")
#Cобытия
@client.event
async def on_member_join(member):
    role = get(member.guild.roles, name=ROLE)
    await member.add_roles(role)
    print(f"{member} was given {role}")

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('очке Димы'))
    print('Bot is ready.')

#Команды для фана
@client.command(aliases=['d'])
async def dice(ctx):
    dice = ['1','2','3','4','5','6']
    await ctx.send(f'Бросаю кубики\nВыпало: {random.choice(dice)} и {random.choice(dice)} ')

@client.command(aliases=['ball','8'])
async def _8ball(ctx, * , question):
    responses = ['Да это так.',
    'Насколько я вижу - да.',
    'Наиболее вероятно.',
    'Знаки указывают что да.',
    'Перспектива хорошая.',
    'Абсолютно.',
    'ДА!',
    'Это бесспорно.',
    'Определённо да.',
    'Да это так.',
    'Без сомнения.',
    'Мои источники говорят да.',
    'Может быть.',
    'Лучше сейчас не говорить тебе.',
    'Ты можешь надеяться на это.',
    'Очень сомневаюсь.',
    'Знаки указывают что нет.',
    'Я так не думаю.',
    'Мои источники говорят нет.',
    'Извини, нет.',
    'Не расчитывай на это.',
    'Перспектива не очень хорошая.',
    'Спроси позже.',
    'Не могу сейчас сказать.',
    'Соберись с мыслями и спроси снова.']
    await ctx.send(f'Вопрос: {question}\nОтвет: {random.choice(responses)}')

@client.command(aliases=['delete','del'])
async def clear(ctx, amount=15):
    await ctx.channel.purge(limit=amount) 
    await ctx.send(f'Удалено: {amount}')

@client.command(aliases=[])
async def hug(ctx):
    huggif = ["""https://tenor.com/view/animated-snuggle-cute-hug-gif-8330887""",
    """https://media.tenor.com/images/11157eb0fe0b7b0f296a8066dffa39a7/tenor.gif""",
    """https://tenor.com/view/hug-anime-gif-7552075""",
    """https://tenor.com/view/anime-hug-sweet-love-gif-14246498""",
    """https://tenor.com/view/hug-cuddle-comfort-love-friends-gif-5166500""",
    """https://tenor.com/view/anime-bed-bedtime-sleep-night-gif-12375072""",
    """https://tenor.com/view/loli-lolita-anime-kawaii-sad-gif-5640885"""]
    await ctx.send(f'Держи обнимашки\n{random.choice(huggif)} ' + ctx.message.author.mention)

@client.command(aliases=[])
async def slap(ctx):
    react = ["Закрой еблет",
     "Лови","НЫА!!!",
     "Ща как уебу ска",
      "А по жопе"]
    slapgif = ["""https://tenor.com/view/batman-slap-robin-gif-10206784""",
    """https://tenor.com/view/gap-slapped-knockout-punch-gif-5122019""",
    """https://tenor.com/view/slap-bears-gif-10422113""",
    """https://tenor.com/view/about-to-slap-had-enough-shut-up-shut-it-mostly-sane-gif-14128541""",
    """https://tenor.com/view/tom-and-jerry-slap-slapping-butt-slap-spanking-gif-4517373"""]
    await ctx.send(f'{random.choice(react)}\n{random.choice(slapgif)} ' + ctx.message.author.mention)

@client.command(aliases=['aquo'])
async def addquote(ctx, *, quote): 
    quo = open('quotes.txt','a')
    quo.writelines(quote +' Цитата: ' + ctx.message.author.mention)
    quo.writelines('\n')
    quo.close()

@client.command(aliases=['quo'])
async def quote(ctx):
 await ctx.send(random.choice(list(open('quotes.txt'))))

#Хентай-команда
@client.command(aliases=['nsfw'])
async def gel(ctx, *, arg):
    extremeFiltering = False
    # if isExplicitlyFiltered(ctx, arg):
    #     await ctx.send("Invalid tag entered in request.")
    #     return False
        
    if(ClientConnector.isChannelFiltered(ctx.guild.id)):
        extremeFiltering = False
        if not ChannelFilter.isArgClean(arg.split(' ')):
            await ctx.send("Такое смотреть нельзя!")
            return False #breaks out from executing the command any further
    
    userLimited = True
    if(gelbooruLimiter.checkIfLimited(str(ctx.message.author)) == False):
        userLimited = False
        gelbooruLimiter.limitUser(str(ctx.message.author))

    caller = gelbooruCaller(ctx, apiToken, arg)
    caller.setArgs()
    caller.makeRequest(extremeFiltering)
    response = caller.getContent()

    if not userLimited:
        if response != None:
            auditor.audit(str(ctx.message.author), response["auditMessage"][0], response["auditMessage"][1], "gelbooru")
            await ctx.send(response["response"])
            userStats.updateStats(str(ctx.message.author))
            if(response["sendTags"]):
                await ctx.send("Я нашла для тебя картинку по этим тегам!Радуйся ,чертов дрочер: \n```" + response["tags"]+"```\n")
        else:
            await ctx.send("У такого тега несуществует изображения, попробуй еще раз, больной ублюдок, " + ctx.message.author.mention)
    elif arg==0:
        await ctx.send("Бака!Ты забыл написать тэг UwU " + ctx.message.author.mention)

#Музыкальные-команды

@client.command(pass_context=True, aliases=['j', 'joi'])
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice is not None:
        return await voice.move_to(channel)

    await channel.connect()

    await ctx.send(f"Подключилась к {channel}")

@client.command(pass_context=True, aliases=['l', 'lea'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The client has left {channel}")
        await ctx.send(f"Покинула {channel}")
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("Я не подключена")

@client.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, *url: str):
     
    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("No more queued song(s)\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Song done, playing next queued\n")
                print(f"Songs still in queue: {still_q}")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07

            else:
                queues.clear()
                return

        else:
            queues.clear()
            print("No songs were queued before the ending of the last song\n")



    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("Песня уже играет")
        return


    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("Removed old Queue Folder")
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder")

    await ctx.send("Готовлюсь включать")

    voice = get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': False,
        'outtmpl': "./song.mp3",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    song_search = " ".join(url)

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            ydl.download([f"ytsearch1:{song_search}"])
    except:
        print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL)")
        c_path = os.path.dirname(os.path.realpath(__file__))
        system("spotdl -ff song -f " + '"' + c_path + '"' + " -s " + song_search)

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

@client.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Песня приостановлена")
    else:
        print("Music not playing failed pause")
        await ctx.send("Песен нет нечего ставить на паузу")

@client.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("Песня возобновлена")
    else:
        print("Music is not paused")
        await ctx.send("Песня не оставновлена ,что бы её возобновлять")

@client.command(pass_context=True, aliases=['s', 'sto'])
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    queues.clear()

    queue_infile = os.path.isdir("./Queue")
    if queue_infile is True:
        shutil.rmtree("./Queue")

    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("Песня остановлена")
    else:
        print("No music playing failed to stop")
        await ctx.send("Песен нет - нечего останавливать")

queues = {}

@client.command(pass_context=True, aliases=['q', 'que'])
async def queue(ctx, *url: str):
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    song_search = " ".join(url)

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            ydl.download([f"ytsearch1:{song_search}"])
    except:
        print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if Spotify URL)")
        q_path = os.path.abspath(os.path.realpath("Queue"))
        system(f"spotdl -ff song{q_num} -f " + '"' + q_path + '"' + " -s " + song_search)


    await ctx.send("Добавляю песню " + str(q_num) + " в очередь")

    print("Song added to queue\n")

@client.command(pass_context=True, aliases=['n', 'nex'])
async def next(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Playing Next Song")
        voice.stop()
        await ctx.send("Следующая песня")
    else:
        print("No music playing")
        await ctx.send("Песен нет")

@client.command(pass_context=True, aliases=['v', 'vol'])
async def volume(ctx, volume: int):

    if ctx.voice_client is None:
        return await ctx.send("Не подключена к голосовому каналу")

    print(volume/100)

    ctx.voice_client.source.volume = volume / 100
    await ctx.send(f"Громкость выставлена на {volume}%")

client.run("NjA1MDM1NDE2MjAyMjQ4MjE2.XUWOeQ.gdMeIG2IpPSrE-pqI0cEjPglvO0")
