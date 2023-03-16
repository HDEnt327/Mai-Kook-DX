import json
import io

from datetime import datetime
from khl import Bot, Message, PublicTextChannel, api
from khl.card import CardMessage, Card, Module, Element, Types, Struct
from plugins.maimai_best_50 import generate50
from plugins.maimai_best_40 import generate



with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

bot = Bot(token=config['token'])



@bot.command(name='delete')
async def delete(bot: Bot, msg: Message):
    # print('[LISTEN] DELETE Action request received')
    channel = msg.ctx.channel
    messageList = await PublicTextChannel.list_messages(channel)
    id_list = []
    for items in messageList['items']:
        id_list.append(items['id'])
    for ids in id_list:
        await bot.client.gate.exec_req(api.Message.delete(ids))
    current_date_and_time = datetime.now()
    print('[WORKER] DELETE Done', current_date_and_time)
    await msg.ctx.channel.send('此频道可以通过/delete一键清空')
    # print('[WORKER] DELETE Message sent')



@bot.command(name="b50")
async def b50(msg: Message, username: str = ""):
    if username == "":
        print('[SEARCH] B50 Initiated user search')
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


@bot.command(name="b40")
async def b40(msg: Message, username: str = ""):
    if username == "":
        print('[SEARCH] B40 Initiated user search')
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


async def searchUser(userid: str, filename='binddata.json') -> str:
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        for user in file_data['bind_users']:
            if (userid == user['user_id']):
                return user['user_Pname']
        return 'USERNOTFOUND'



@bot.command(name='bind')
async def bind(bot: Bot, msg: Message, username: str):
    print('[LISTEN] BIND Action request received')
    bindid = msg.author_id
    data = {"user_Pname": username, "user_id": bindid}
    if ((await searchUser(bindid) != 'USERNOTFOUND')):
        await msg.ctx.channel.send("你已经绑定过了，请使用/unbind解绑后重新绑定")
        print('[SEARCH] BIND User has already binded')
        print('[ABORT]')
        return
    print('[WORKER] BIND Data preparation complete')    
    await write_userData(data)
    print('[WORKER] BIND JSON Write complete')
    await msg.ctx.channel.send('Bind Complete!')
    print('[WORKER] BIND Message sent')

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

async def write_userData(new_data, filename='binddata.json'):
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        file_data["bind_users"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)

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
    c1.append(Module.Divider())
    c1.append(Module.Section(Element.Text('更多功能编写中')))
    cm.append(c1)
    print('[CARD WORKER] Card message build complete')
    await msg.reply(cm)
    print('[CARD WORKER] Message sent')



bot.run()









