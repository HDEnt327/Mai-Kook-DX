import json
import io

from datetime import datetime
from khl import Bot, Message, PublicTextChannel, api
from khl.card import CardMessage, Card, Module, Element, Types, Struct
from plugins.maimai_best_50 import generate50
from plugins.maimai_best_40 import generate
from plugins.image import *
from plugins.tool import hash
from plugins.maimaidx_music import *
import re


with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

bot = Bot(token=config['token'])


# Deletes all messages in a text channel
@bot.command(name='delete')
async def delete(bot: Bot, msg: Message):
    print('[LISTEN] DELETE Action request received')
    # Define channel to be searched
    channel = msg.ctx.channel
    messageList = await PublicTextChannel.list_messages(channel)
    id_list = []
    # Append message ids to idlist
    for items in messageList['items']:
        id_list.append(items['id'])
    # Delete messages according to ids
    for ids in id_list:
        await bot.client.gate.exec_req(api.Message.delete(ids))
    current_date_and_time = datetime.now()
    print('[WORKER] DELETE Done', current_date_and_time)
    await msg.ctx.channel.send('此频道可以通过/delete一键清空')
    print('[WORKER] DELETE Message sent')
    print('[DONE]')


# Generate and send b50
@bot.command(name="b50")
async def b50(msg: Message, username: str = ""):
    if username == "":
        print('[LISTEN] B50 Initiated user search')
        searchres = await searchUser(msg.author_id)
        if searchres == 'USERNOTFOUND':
            print('[SEARCH] B50 User has not binded yet')
            await msg.ctx.channel.send('你还没有绑定账号')
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




@bot.command(name='查歌')
async def query_chart(bot: Bot, message: Message, songid: str, chartlvl: str = ''):
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
            image = get_cover_len4_id(music['id']) + '.png'
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
            c1.append(Module.Divider())
            c1.append(Module.Section(Element.Text(msg), accessory=Element.Image(src=img_url), mode=Types.SectionMode.RIGHT))
            # Big image mode
            # c1.append(Module.Section(Element.Text(f"{music['id']}. {music['title']}\n")))
            # c1.append(Module.Container(Element.Image(src=img_url)))
            # c1.append(Module.Section(Element.Text(msg)))
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
        name = songid
        music = total_list.by_id(name)
        print('[WORKER] QUERY Music FOUND')
        image = get_cover_len4_id(music['id']) + '.png'
        print('[WORKER] QUERY Image file GET')
        try:
            img_url = await bot.client.create_asset('src/static/mai/cover/' + image)
            cm = CardMessage()
            c1 = Card(Module.Header(f"{music['id']}. {music['title']}\n"))
            c1.append(Module.Divider())
            c1.append(Module.Section(Element.Text(f"艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['from']}\n难度: {'/'.join(music['level'])}"), accessory=Element.Image(src=img_url), mode=Types.SectionMode.RIGHT))
            # Big image mode
            # c1.append(Module.Section(Element.Text(f"{music['id']}. {music['title']}\n")))
            # c1.append(Module.Container(Element.Image(src=img_url)))
            # c1.append(Module.Section(Element.Text(f"艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['from']}\n难度: {'/'.join(music['level'])}")))
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


@bot.command(name='查询')
async def search_music(bot: Bot, message: Message, search: str = ''):
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



@bot.command(name='phelp')
async def help(msg: Message):
    print('[LISTEN] HELP Action request received')
    cm = CardMessage()
    c1 = Card(Module.Header('PhiEditer Bot HELP'))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('**maimai相关**')))
    c1.append(Module.Section(Element.Text('`/bind [查分器id]` 绑定账号')))
    c1.append(Module.Section(Element.Text('`/unbind` 解绑账号')))
    c1.append(Module.Section(Element.Text('`/b40 <查分器id>` 查询B40')))
    c1.append(Module.Section(Element.Text('`/b50 <查分器id>` 查询B50')))
    c1.append(Module.Section(Element.Text('绑定账号后查询B40/B50不必再输入查分器id')))
    c1.append(Module.Section(Element.Text('`/查询 [关键词]` 查询歌曲')))
    c1.append(Module.Section(Element.Text('`/查歌 [歌曲id] <难度>` 歌曲或谱面')))
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('更多功能编写中')))
    cm.append(c1)
    print('[CARD WORKER] Card message build complete')
    await msg.reply(cm)
    print('[CARD WORKER] Message sent')
    print('[DONE]')

# Pings bot
@bot.command(name='ping')
async def ping(msg: Message):
    print('[LISTEN] PING Initiasted')
    await msg.reply('勢いよく叩いたり、スライドさせたりしないでください。')
    print('[WORKER] Message sent')

bot.run()
