import requests
import json

from datetime import datetime

def bmrequest(url="http://bot.gekj.net/api/v1/online.bot"):
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    uuid = config.get('BMuuid', '')
    if not uuid:
        print("[ERROR] No UUID found in config.json")
        return
    current_date_and_time = datetime.now()
    print("[REQUEST] Making timed request to botmarket")
    response = requests.post(url=url, headers={'UUID': uuid})
    rpContent = response.content.decode('utf-8')
    rpJSON = json.loads(rpContent)
    print("[REQUEST] " + str(current_date_and_time) + " RESPONSE: " + rpJSON['msg'] + " CODE: " + str(rpJSON['codeNum']))