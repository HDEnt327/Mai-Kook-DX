import requests
import json

from datetime import datetime

def bmrequest(uuid = "081b6e3b-fcaa-48a5-b9ba-90f93dab7b84", url="http://bot.gekj.net/api/v1/online.bot"):
    current_date_and_time = datetime.now()
    print("[REQUEST] Making timed request to botmarket")
    response = requests.post(url=url, headers={'UUID': uuid})
    rpContent = response.content.decode('utf-8')
    rpJSON = json.loads(rpContent)
    print("[REQUEST] " + str(current_date_and_time) + " RESPONSE: " + rpJSON['msg'] + " CODE: " + str(rpJSON['codeNum']))