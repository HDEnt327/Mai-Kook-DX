import json
import io
import time
import logging
import sys
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from khl import Bot, Message, PublicTextChannel, api, MessageTypes
from khl.card import CardMessage, Card, Module, Element, Types, Struct
from plugins.maimai_best_50 import generate50
from plugins.maimai_best_40 import generate
from plugins.image import *
from plugins.tool import hash
from plugins.maimaidx_music import *
from bmrequest import bmrequest


with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

botToken = config['token']
if not botToken:
    print('[ERROR] No bot token found in config.json')
    sys.exit(1)


bot = Bot(token=config['token'])

useBM = config['useBM']
if useBM:
    print('[INIT] BotMarket enabled')
    sched = BackgroundScheduler()
    bmrequest()
    sched.add_job(bmrequest, 'interval', minutes=30)
    sched.start()

# FIX LOGGER LATER
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# logHandler = logging.FileHandler('logs.log')
# logHandler.setLevel(logging.INFO)
# logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# TEMP LOGGER FOR NOW
logging.basicConfig(filename='logs.log', encoding='utf-8', level=logging.DEBUG, format='%(levelname)s - %(asctime)s - %(name)s - %(message)s')

print('[INIT] Bot started')



# Generate and send b50
# Calls for Generate50 Written by Diving-Fish
@bot.command(name="b50")
async def b50(msg: Message, username: str = ""):
    current_date_and_time = datetime.now()
    print('[LISTEN] ' + str(current_date_and_time))
    if username == "":
        print('[LISTEN] B50 Initiated user search')
        searchres = await searchUser(msg.author_id)
        if searchres == 'USERNOTFOUND':
            print('[SEARCH] B50 User has not binded yet')
            await msg.ctx.channel.send('你还没有绑定账号，请使用/bind绑定账号')
            print('[ABORT]')
            return
        payload = {'username': searchres,'b50':True}
        print('[SEARCH] B50 Search done')
        print('[SEARCH] B50 Search result: ' + searchres)
    else:
        payload = {'username': username,'b50':  True}
    img, success = await generate50(payload)
    if success == 400:
        print('[WORKER] B50 USER NOT FOUND')
        await msg.ctx.channel.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
        print('[WORKER] B50 Message sent')
        print('[ABORT]')
    elif success == 403:
        await msg.ctx.channel.send("该用户禁止了其他人获取数据。")
    else:
        print('[WORKER] B50 USER FOUND')
        print('[LISTEN] B50 Action request received')
        print('[WORKER] B50 Image processing...')
        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format='PNG')
        imgByte = io.BytesIO(imgByteArr.getvalue())
        img_url = await bot.client.create_asset(imgByte)
        print('[WORKER] B50 Image processing... DONE!')
        print('[CARD WORKER] Card message building...')
        cm = CardMessage()
        c1 = Card(Module.Header('你的B50'))
        c1.append(Module.Divider())
        c1.append(Module.Container(Element.Image(src=img_url)))
        cm.append(c1)
        print('[CARD WORKER] Card message building... DONE!')
        await msg.reply(cm)
        print('[CARD WORKER] Message sent')
        print('[DONE]')


@bot.command(name="b40")
async def b40(msg: Message, username: str = ""):
    current_date_and_time = datetime.now()
    print('[LISTEN] ' + str(current_date_and_time))
    if username == "":
        print('[LISTEN] B40 Initiated user search')
        searchres = await searchUser(msg.author_id)
        if (searchres == 'USERNOTFOUND'):
            print('[SEARCH] B40 User has not binded yet')
            await msg.ctx.channel.send('你还没有绑定账号')
            print('[ABORT]')
            return
        payload = {'username': searchres}
        print('[SEARCH] B40 Search done')
        print('[SEARCH] B40 Search result: ' + searchres)
    else:
        payload = {'username': username}
    img, success = await generate(payload)
    if success == 400:
        print('[WORKER] B40 USER NOT FOUND')
        await msg.ctx.channel.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
        print('[WORKER] B40 Message sent')
        print('[ABORT]')
    elif success == 403:
        await msg.ctx.channel.send("该用户禁止了其他人获取数据。")
    else:
        print('[WORKER] B40 USER FOUND')
        print('[LISTEN] B40 Action request received')
        print('[WORKER] B40 Image processing...')
        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format='PNG')
        imgByte = io.BytesIO(imgByteArr.getvalue())
        img_url = await bot.client.create_asset(imgByte)
        print('[WORKER] B40 Image processing... DONE!')
        print('[CARD WORKER] Card message building...')
        cm = CardMessage()
        c1 = Card(Module.Header('你的B40'))
        c1.append(Module.Divider())
        c1.append(Module.Container(Element.Image(src=img_url)))
        cm.append(c1)
        print('[CARD WORKER] Card message building... DONE!')
        await msg.reply(cm)
        print('[CARD WORKER] Message sent')
        print('[DONE]')


# Searches for user according to user KOOK id and returns prober id
# id binds are stored in binddata.json
async def searchUser(userid: str, filename='binddata.json') -> str:
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        for user in file_data['bind_users']:
            if (userid == user['user_id']):
                return user['user_Pname']
        return 'USERNOTFOUND'


# Bind KOOK id with prober id
@bot.command(name='bind')
async def bind(bot: Bot, msg: Message, username: str = "NO_PARAM"):
    current_date_and_time = datetime.now()
    print('[LISTEN] ' + str(current_date_and_time))
    print('[LISTEN] BIND Action request received')
    bindid = msg.author_id
    data = {"user_Pname": username, "user_id": bindid}
    if ((await searchUser(bindid) != 'USERNOTFOUND')):
        await msg.ctx.channel.send("你已经绑定过了，请使用/unbind解绑后重新绑定")
        print('[SEARCH] BIND User has already binded')
        print('[ABORT]')
        return
    if (username == "NO_PARAM"):
        await msg.ctx.channel.send('Error: NO_PARAM，请在/bind后面填写查分器id')
        print('[WORKER] BIND NO PARAMETER ENTERED')
        print('[WORKER] BIND Message sent')
        print('[ABORT]')
        return
    print('[WORKER] BIND Data preparation complete')    
    await write_userData(data)
    print('[WORKER] BIND JSON Write complete')
    await msg.ctx.channel.send('Bind Complete!')
    print('[WORKER] BIND Message sent')
    print('[DONE]')

# Unbind KOOK id with prober id
@bot.command(name='unbind')
async def unbind(bot: Bot, msg: Message):
    current_date_and_time = datetime.now()
    print('[LISTEN] ' + str(current_date_and_time))
    print('[LISTEN] UNBIND Action request received')
    unbindid = msg.author_id
    if ((await searchUser(unbindid) == 'USERNOTFOUND')):
        await msg.ctx.channel.send("你还没有绑定查分器账号，请使用/bind绑定")
        print('[SEARCH] UNBIND User has not binded yet')
        print('[ABORT]')
        return
    print('[WORKER] UNBIND Data preparation complete')    
    print('[WORKER] UNBIND Start user search')
    await unwrite_userData(unbindid)
    print('[WORKER] UNBIND JSON Write complete')
    await msg.ctx.channel.send('Unbind Complete!')
    print('[WORKER] UNBIND Message sent')
    print('[DONE]')

# Appends new user id
async def write_userData(new_data, filename='binddata.json'):
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        file_data["bind_users"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)

# Deletes user id
async def unwrite_userData(userid: str, filename='binddata.json'):
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        print('looking for ' + userid)
        for i in range(len(file_data['bind_users'])):
            print(file_data['bind_users'][i]['user_id'])
            if file_data['bind_users'][i]['user_id'] == userid:
                print('User Found!')
                file_data['bind_users'].pop(i)
                break
    with open(filename, 'w') as file:
        file.seek(0)
        json.dump(file_data, file, indent=4)


# Query for chart or song
@bot.command(name='查歌')
async def query_chart(bot: Bot, message: Message, songid: str, chartlvl: str = '', mode: str = "small"):
    current_date_and_time = datetime.now()
    print('[LISTEN] ' + str(current_date_and_time))
    print('[LISTEN] QUERY Initiated')
    level_labels = ['绿', '黄', '红', '紫', '白']
    if chartlvl != "":
        try:
            level_index = level_labels.index(chartlvl)
            level_name = ['Basic', 'Advanced', 'Expert', 'Master', 'Re: MASTER']
            name = songid
            music = total_list.by_id(name)
            print('[WORKER] QUERY Music FOUND')
            chart = music['charts'][level_index]
            print('[WORKER] QUERY Chart GET')
            ds = music['ds'][level_index]
            print('[WORKER] QUERY Constant GET')
            level = music['level'][level_index]
            print('[WORKER] QUERY Level SET')
            image = get_cover_len5_id(music['id']) + '.png'
            print('[WORKER] QUERY Image file GET')
            if len(chart['notes']) == 4:
                print('[WORKER] QUERY Chart type = STANDARD')
                msg = f'''{level_name[level_index]} {level}({ds})
                TAP: {chart['notes'][0]}
                HOLD: {chart['notes'][1]}
                SLIDE: {chart['notes'][2]}
                BREAK: {chart['notes'][3]}
                谱师: {chart['charter']}'''
                print('[WORKER] QUERY Message build complete')
            else:
                print('[WORKER] QUERY Chart type = DELUXE')
                msg = f'''{level_name[level_index]} {level}({ds})
                TAP: {chart['notes'][0]}
                HOLD: {chart['notes'][1]}
                SLIDE: {chart['notes'][2]}
                TOUCH: {chart['notes'][3]}
                BREAK: {chart['notes'][4]}
                谱师: {chart['charter']}'''
                print('[WORKER] QUERY Message build complete')
            img_url = await bot.client.create_asset('src/static/mai/cover/' + image)
            print('[CARD WORKER] QUERY Image asset created')
            cm = CardMessage()
            c1 = Card(Module.Header(f"{music['id']}. {music['title']}\n"))
            if mode == "small":
                c1.append(Module.Divider())
                c1.append(Module.Section(Element.Text(msg), accessory=Element.Image(src=img_url), mode=Types.SectionMode.RIGHT))
            # Big image mode
            # c1.append(Module.Section(Element.Text(f"{music['id']}. {music['title']}\n")))
            elif mode == "large" or mode == "big":
                c1.append(Module.Container(Element.Image(src=img_url)))
                c1.append(Module.Section(Element.Text(msg)))
            cm.append(c1)
            print('[CARD WORKER] QUERY Card build complete!')
            await message.reply(cm)
            print('[CARD WORKER] QUERY CardMessage sent!')
            print('[DONE]')
        except Exception:
            print('[WORKER] QUERY MAP NOT FOUND')
            await message.reply("未找到该谱面")
            print('[WORKER] Message sent')
            print('[ABORT]')
    else:
        try:
            name = songid
            music = total_list.by_id(name)
            print(music)
            print('[WORKER] QUERY Music FOUND')
            image = get_cover_len5_id(music['id']) + '.png'
            print('[WORKER] QUERY Image file GET')
            img_url = await bot.client.create_asset('src/static/mai/cover/' + image)
            cm = CardMessage()
            c1 = Card(Module.Header(f"{music['id']}. {music['title']}\n"))
            msg = f"艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['from']}\n难度: {'/'.join(music['level'])}"
            if mode == "small":
                c1.append(Module.Divider())
                c1.append(Module.Section(Element.Text(msg), accessory=Element.Image(src=img_url), mode=Types.SectionMode.RIGHT))
            # Big image mode
            # c1.append(Module.Section(Element.Text(f"{music['id']}. {music['title']}\n")))
            elif mode == "large" or mode == "big":
                c1.append(Module.Container(Element.Image(src=img_url)))
                c1.append(Module.Section(Element.Text(msg)))
            cm.append(c1)
            print('[CARD WORKER] QUERY Card build complete!')
            await message.reply(cm)
            print('[CARD WORKER] QUERY CardMessage sent!')
            print('[DONE]')
        except Exception:
            print('[WORKER] QUERY SONG NOT FOUND')
            await message.reply("未找到该乐曲")
            print('[WORKER] Message sent')
            print('[ABORT]')


# Query for chart/map
@bot.command(name='查询')
async def search_music(bot: Bot, message: Message, search: str = ''):
    current_date_and_time = datetime.now()
    print('[LISTEN] ' + str(current_date_and_time))
    print('[LISTEN] SEARCH Initiated')
    name = search
    if name == "":
        print('[WORKER] SEARCH NO PARAM')
        await message.reply('请输入搜索关键词')
        print('[WORKER] Message sent')
        print('[ABORT]')
        return
    res = total_list.filter(title_search=name)
    if len(res) == 0:
        await message.reply("没有找到这样的乐曲。")
    elif len(res) < 50:
        search_result = ""
        for music in sorted(res, key = lambda i: int(i['id'])):
            search_result += f"{music['id']}. {music['title']}\n"
        cm = CardMessage()
        c1 = Card(Module.Header('查询结果'))
        c1.append(Module.Divider())
        c1.append(Module.Section(Element.Text(search_result)))
        cm.append(c1)
        print('[CARD WORKER] SEARCH Card build complete!')
        await message.reply(cm)
        print('[CARD WORKER] SEARCH CardMessage sent!')
        print('[DONE]')
    else:
        await message.reply(f"结果过多（{len(res)} 条），请缩小查询范围。")

@bot.command(name='分数列表')
async def level_score_list(message: Message, level: str = '', page: int = 1):
    current_date_and_time = datetime.now()
    print('[LISTEN] ' + str(current_date_and_time))
    print(f'[LISTEN] LEVEL LIST Action request received: {message.content}')
    username = await searchUser(message.author_id)
    print('[WORKER] LEVEL LIST User found')
    print('[WORKER] LEVEL LIST User: ' + username)
    payload = {'username': username}
    payload['version'] = list(set(version for version in {'初': 'maimai',
                                                        '真': 'maimai PLUS',
                                                        '超': 'maimai GreeN',
                                                        '檄': 'maimai GreeN PLUS',
                                                        '橙': 'maimai ORANGE',
                                                        '暁': 'maimai ORANGE PLUS',
                                                        '晓': 'maimai ORANGE PLUS',
                                                        '桃': 'maimai PiNK',
                                                        '櫻': 'maimai PiNK PLUS',
                                                        '樱': 'maimai PiNK PLUS',
                                                        '紫': 'maimai MURASAKi',
                                                        '菫': 'maimai MURASAKi PLUS',
                                                        '堇': 'maimai MURASAKi PLUS',
                                                        '白': 'maimai MiLK',
                                                        '雪': 'MiLK PLUS',
                                                        '輝': 'maimai FiNALE',
                                                        '辉': 'maimai FiNALE',
                                                        '熊': 'maimai でらっくす',
                                                        '華': 'maimai でらっくす PLUS',
                                                        '华': 'maimai でらっくす PLUS',
                                                        '爽': 'maimai でらっくす Splash',
                                                        '煌': 'maimai でらっくす Splash PLUS',
                                                        '宙': 'maimai でらっくす UNiVERSE',
                                                        '星': 'maimai でらっくす UNiVERSE PLUS',
                                                        'fes': 'maimai でらっくす FESTiVAL',
                                                        'fesp': 'maimai でらっくす FESTiVAL PLUS'
    }.values()))
    diffs = {1: 'BASIC', 2: 'ADVANCED', 3: 'EXPERT', 4: 'MASTER', 5: 'RE:MASTER'}
    with requests.request('POST', 'https://www.diving-fish.com/api/maimaidxprober/query/plate', json=payload) as resp:
        response = resp.json()
        song_list = []
        for song in response['verlist']:
            if song['level'] == str(level):
                song_list.append(song)
        page = max(min(int(page), len(song_list) // 50 + 1), 1) if page else 1
        msg = f'您的{level}分数列表（从高至低）：\n'
        for i, s in enumerate(sorted(song_list, key=lambda i: i['achievements'], reverse=True)):
            if (page - 1) * 50 <= i < page * 50:
                # m = mai.total_list.by_id(str(s['id']))
                msg += f'No.{i + 1} {s["achievements"]:.4f}% {s["id"]}. {s["title"]} {diffs[s["level_index"]+1]} ({s["type"]})'
                if s["fc"] == 'fc': msg += ' (FC)'
                elif s["fc"] == 'ap': msg += ' (AP)'
                elif s["fc"] == 'fcp': msg += ' (FC+)'
                elif s["fc"] == 'app': msg += ' (AP+)'
                if s["fs"] == 'fs': msg += ' (FS)'
                elif s["fs"] == 'fsp': msg += ' (FS+)'
                msg += '\n'
        msg += f'第{page}页，共{len(song_list) // 50 + 1}页'
        print('[WORKER] LEVEL LIST Message build complete!')
        cm = CardMessage()
        c1 = Card(Module.Header('查询结果'))
        c1.append(Module.Divider())
        c1.append(Module.Section(Element.Text(msg)))
        cm.append(c1)
        print('[CARD WORKER] LEVEL LIST Card build complete!')
        await message.reply(cm)
        print('[CARD WORKER] LEVEL LIST CardMessage sent!')
        print('[DONE]')


@bot.command(name='随机野史')
async def random_history(msg: Message):
    print("[LISTEN] " + str(datetime.now()))
    print("[LISTEN] RANDOM HISTORY Action request received")
    # read history.json and randomly pick an entry and reply the 'content'
    with open('history.json', 'r', encoding='utf-8') as f:
        history = json.load(f)['history']
        entry = history[random.randint(1, len(history)-1)]
        await msg.reply(entry['content'])
        print("[WORKER] RANDOM HISTORY Message sent")
        print("[DONE]")

@bot.command(name='提交野史')
async def submit_history(msg: Message, *args):
    print("[LISTEN] " + str(datetime.now()))
    print("[LISTEN] HISTORY SUBMIT Action request received")
    # add a new entry to history.json, and reply the 'id'
    content = args[0]
    for x in range(1, len(args)):
        content = content + " " + args[x]
    if content == "":
        await msg.reply('请提供野史内容')
        print("[WORKER] HISTORY SUBMIT No content provided")
        print("[WORKER] HISTORY SUBMIT Message sent")
        print("[ABORT]")
        return
    with open('history.json', 'r', encoding='utf-8') as f:
        history = json.load(f)
        for entry in history['history']:
            if entry['content'] == content:
                print("[WORKER] HISTORY SUBMIT Entry already exists")
                await msg.reply('这个野史已经被记载过了，id是' + str(entry['id']))
                print("[WORKER] HISTORY SUBMIT Message sent")
                print("[ABORT]")
                return
        # find any disconnected id and use it
        id = len(history['history'])
        print("[WORKER] HISTORY SUBMIT Entry not found, creating new entry")
        for i in range(1, len(history['history'])):
            if history['history'][i]['id'] != i:
                id = i
                break
        print("[WORKER] HISTORY SUBMIT Using existing id: " + str(id))
        entry = {'id': id, 'submitter': msg.author_id, 'content': content}
        history['history'].insert(id, entry)
    with open('history.json', 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
    print("[WORKER] HISTORY SUBMIT Entry added")
    await msg.reply(f'野史记载成功，野史id: {entry["id"]}')
    print("[WORKER] HISTORY SUBMIT Message sent")
    print("[DONE]")
        
@bot.command(name='查询野史')
async def query_history(msg: Message, id: int):
    print("[LISTEN] " + str(datetime.now()))
    print("[LISTEN] HISTORY QUERY Action request received")
    # read history.json and reply the 'content' of the entry with 'id'
    with open('history.json', 'r', encoding='utf-8') as f:
        history = json.load(f)['history']
        for entry in history:
            if entry['id'] == id:
                print("[WORKER] HISTORY QUERY Entry found")
                await msg.reply(entry['content'])
                print("[WORKER] HISTORY QUERY Message sent")
                print("[DONE]")
                return
        await msg.reply('未找到这个野史')
        print("[WORKER] HISTORY QUERY Entry not found")
        print("[WORKER] HISTORY QUERY Message sent")
        print("[ABORT]")

@bot.command(name='删除野史')
async def delete_history(msg: Message, id: int):
    print("[LISTEN] " + str(datetime.now()))
    print("[LISTEN] HISTORY DELETE Action request received")
    # delete the entry with 'id' from history.json
    if id == 0:
        await msg.reply('无法删除这个野史或野史未记载')
        print("[WORKER] HISTORY DELETE Invalid id")
        print("[WORKER] HISTORY DELETE Message sent")
        print("[ABORT]")
        return
    with open('history.json', 'r', encoding='utf-8') as f:
        history = json.load(f)
        for entry in history['history']:
            if entry['id'] == id:
                if entry['submitter'] != msg.author_id:
                    await msg.reply('你没有权限删除这个野史')
                    print("[WORKER] HISTORY DELETE No permission")
                    print("[WORKER] HISTORY DELETE Message sent")
                    print("[ABORT]")
                    return
                print("[WORKER] HISTORY DELETE Entry found")
                history['history'].remove(entry)
                print("[WORKER] HISTORY DELETE Entry removed")
                with open('history.json', 'w', encoding='utf-8') as f:
                    json.dump(history, f, ensure_ascii=False, indent=4)
                await msg.reply('野史删除成功')
                print("[WORKER] HISTORY DELETE Message sent")
                print("[DONE]")
                return
        await msg.reply('未找到这个野史')
        print("[WORKER] HISTORY DELETE Entry not found")
        print("[WORKER] HISTORY DELETE Message sent")
        print("[ABORT]")


# Help menu
# Prioritize reference to wiki page
@bot.command(name='mhelp')
async def help(msg: Message):
    current_date_and_time = datetime.now()
    print('[LISTEN] ' + str(current_date_and_time))
    print('[LISTEN] HELP Action request received')
    cm = CardMessage()
    c1 = Card(Module.Header('Mai-Kook-DX Help Menu'))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('***第一次使用强烈建议阅读使用文档：[点此进入](https://github.com/HDEnt327/Mai-Kook-DX/wiki)***')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('**NEW：随机野史**')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('`/随机野史` 随机获取一条野史')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('`/提交野史 [内容]` 提交一条野史')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('`/查询野史 [id]` 查询一条野史')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('`/删除野史 [id]` 删除一条野史（仅限提交者）')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('**查分**')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('`/bind [查分器id]` 绑定账号\n如：`/bind Example123`')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('`/unbind` 解绑账号')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('`/b40 <查分器id>` 查询B40\n如：`/b40 Example123`\n如果绑定了查分器账号可直接：`/b40`')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('`/b50 <查分器id>` 查询B50\n如：`/b50 Example123`\n如果绑定了查分器账号可直接：`/b50`')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('(experimental) `/分数列表 [难度] <页数>` 查询分数列表\n如：`/分数列表 15 1` 或：`/分数列表 15`')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('绑定账号后查询不必再输入查分器id')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('**查歌/查谱面**')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('`/查询 [关键词]` 查询歌曲\n如：`/查询 MAXRAGE`')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('`/查歌 [歌曲id] <难度>` 查歌曲或谱面\n如：`/查歌 11102 紫` 或：`/查歌 11102`')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('[ ] 内的内容为必填，<> 内的内容为可填')))
    c1.append(Module.Section(Element.Text('输入参数的时候不必输入 [ ] 和 <>')))
    c1.append(Module.Section(Element.Text('更多功能编写中')))
    cm.append(c1)
    print('[CARD WORKER] Card message build complete')
    await msg.reply(cm)
    print('[CARD WORKER] Message sent')
    print('[DONE]')


@bot.command(name='rasheet')
async def rasheet(msg: Message):
    img_url = await bot.client.create_asset('src/static/mai/rating.jpg')
    await msg.reply(img_url, type=MessageTypes.IMG)

# Pings bot
@bot.command(name='ping')
async def ping(msg: Message):
    current_date_and_time = datetime.now()
    print('[LISTEN] ' + str(current_date_and_time))
    print('[LISTEN] PING Initiated')
    await msg.reply('勢いよく叩いたり、スライドさせたりしないでください。')
    print('[WORKER] Message sent')

# run the bot
bot.run()
