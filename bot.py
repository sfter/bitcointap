import os
import sys
import time
import json
import random
import requests
import argparse
from json import dumps as dp, loads as ld
from datetime import datetime
from colorama import *
from urllib.parse import unquote, parse_qs
from base64 import b64decode

init(autoreset=True)

merah = Fore.LIGHTRED_EX
putih = Fore.LIGHTWHITE_EX
hijau = Fore.LIGHTGREEN_EX
kuning = Fore.LIGHTYELLOW_EX
biru = Fore.LIGHTBLUE_EX
reset = Style.RESET_ALL
hitam = Fore.LIGHTBLACK_EX


class BitcoinTap:
    def __init__(self):
        self.base_headers = {
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
            "content-type": "application/json",
            "origin": "https://rnes.site/",
            "x-requested-with": "org.telegram.messenger",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://rnes.site/",
            "accept-encoding": "gzip, deflate",
            "accept-language": "en,en-US;q=0.9",
        }
        self.garis = putih + "~" * 50

    def check_tasks(self, query_data, user_id, chat_id):
        headers = self.base_headers.copy()
        headers["x-api-key"] = f"{query_data}"
    
        try:
            response = requests.get('https://rnes.site/api/task/', headers=headers)
            if response.status_code == 200:
                tasks = response.json()
                task_results = self.get_events(query_data, user_id, chat_id, tasks)
                for task in tasks:
                    titlenya = task.get('title', None)
                    task_id = task.get('id', None)
                    self.log(f"{Fore.YELLOW+Style.BRIGHT}Checking Task: {titlenya} Lists")
                    task_result = self.get_task_status(task_results, task_id)
                    if task_result:
                        if task_result.get("is_done") == False:
                            self.start_task(query_data, user_id, task_id, titlenya)
                        if task_result.get("is_claim") == False:  
                            self.claim_task(query_data, user_id, task_id, titlenya)
                    else:
                        self.start_task(query_data, user_id, task_id, titlenya)
                        self.claim_task(query_data, user_id, task_id, titlenya)
            else:
                print(f"{Fore.RED+Style.BRIGHT}\nFailed to get tasks")
        except Exception as e:
            print(f"{Fore.RED+Style.BRIGHT}\nFailed to get tasks Error Code: {response.status_code} | {str(e)}")

    def start_task(self, query_data, user_id, task_id, titlenya):
        url = f'https://rnes.site/api/task/event/create/'
        headers = self.base_headers.copy()
        headers["x-api-key"] = f"{query_data}"
        payload = {"user_id":f'{user_id}',"task_id":f'{task_id}',"is_done":"true"}
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 201:
                print(f"{Fore.GREEN+Style.BRIGHT}\nTask {titlenya} started")
            else:
                print(f"{Fore.RED+Style.BRIGHT}\nFailed to start task {titlenya} {response.json()}")
            return 
        except:
            print(f"{Fore.RED+Style.BRIGHT}\nFailed to start task {titlenya} {response.status_code} ")

    def claim_task(self, query_data, user_id, task_id, titlenya):
        url = f'https://rnes.site/api/task/event/create/'
        headers = self.base_headers.copy()
        headers["x-api-key"] = f"{query_data}"
        payload = {"user_id":f'{user_id}',"task_id":f'{task_id}',"is_claim":"true"}
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 201:
                print(f"{Fore.GREEN+Style.BRIGHT}\nTask {titlenya} claimed")
            else:
                print(f"{Fore.RED+Style.BRIGHT}\nFailed to start task {titlenya} {response.json()}")
            return 
        except:
            print(f"{Fore.RED+Style.BRIGHT}\nFailed to start task {titlenya} {response.status_code} ")

    def claim_farming(self, query_data, user_id):
        url = "https://rnes.site/api/click/create/"
        headers = self.base_headers.copy()
        headers["x-api-key"] = f"{query_data}"
        payload = {"user_id":f'{user_id}'}
        self.log(f"{hijau}Claiming farming for {user_id}")
        res = requests.post(url, headers=headers, json=payload)
        balance = res.json().get("received_points", None)
        self.log(f"{hijau}balance after claim : {balance}")
        return

    def connect_wallet_address(self, query_data, user_id, address):
        url = "https://rnes.site/api/wallet/create/"
        headers = self.base_headers.copy()
        headers["x-api-key"] = f"{query_data}"
        payload = {"owner_id":f'{user_id}',"address":f'{address}'}
        self.log(f"{hijau}Claiming farming for {user_id}")
        res = requests.post(url, headers=headers, json=payload)
        return   

    # 返回任务列表的claim状态
    # [
    #     {
    #         "id": 8631,
    #         "user_id": 1144,
    #         "task_id": 2,
    #         "is_done": true,
    #         "is_claim": true,
    #         "received_points": 300
    #     },
    #     {
    #         "id": 8633,
    #         "user_id": 1144,
    #         "task_id": 5,
    #         "is_done": true,
    #         "is_claim": true,
    #         "received_points": 300
    #     }
    # ]
    def get_events(self, query_data, user_id, chat_id, tasks):
        url = "https://rnes.site/api/task/event/"
        headers = self.base_headers.copy()
        headers["x-api-key"] = f"{query_data}"

        resources = []

        for task in tasks:
            resource_id = task.get('resource_id', None)
            task_id = task.get('id', None)
            resources.append({"chat_id": chat_id, "resource_id": resource_id, "task_id": task_id})

        query_params = '?user_id=' + f'{user_id}' + '&resources=' + json.dumps(resources)
        full_url = url + query_params

        res = requests.get(full_url, headers=headers)
        return res.json()

    def get_task_status(self, task_results, task_id):
        for task_result in task_results:
            temp_task_id = task_result.get('task_id', None)
            if task_id == temp_task_id:
                return task_result
        return

    def get_user(self, query_data, chatid):
        url = "https://rnes.site/api/user/?chat_id=" + f'{chatid}'
        headers = self.base_headers.copy()
        headers["x-api-key"] = f"{query_data}"
        res = requests.get(url, headers=headers)
        user_id = res.json()["id"]
        self.log(f"{hijau}user_id : {user_id}")
        return user_id   

    def get_balance(self, query_data, user_id, only_show_balance=False):
        url = "https://rnes.site/api/invited/balance/?owner_id=" + f'{user_id}'
        headers = self.base_headers.copy()
        headers["x-api-key"] = f"{query_data}"
        res = requests.get(url, headers=headers)
        balance = res.json()["claim_balance"]
        self.log(f"{hijau}balance : {putih}{balance}")
        if only_show_balance:
            return
        timestamp = round(res.json()["timestamp"] / 1000)
        if "farming" not in res.json().keys():
            return False, "not_started"
        end_farming = round(res.json()["farming"]["endTime"] / 1000)
        if timestamp > end_farming:
            self.log(f"{hijau}now is time to claim farming !")
            return True, end_farming

        self.log(f"{kuning}not time to claim farming !")
        end_date = datetime.fromtimestamp(end_farming)
        self.log(f"{hijau}end farming : {putih}{end_date}")
        return False, end_farming

    def data_parsing(self, data):
        return {k: v[0] for k, v in parse_qs(data).items()}

    def log(self, message):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{hitam}[{now}]{reset} {message}")

    def get_local_token(self, userid):
        if not os.path.exists('tokens.json'):
            open("tokens.json", "w").write(json.dumps({}))
        tokens = json.loads(open("tokens.json", "r").read())
        if str(userid) not in tokens.keys():
            return False

        return tokens[str(userid)]

    def save_local_token(self, userid, token):
        tokens = json.loads(open("tokens.json", "r").read())
        tokens[str(userid)] = token
        open("tokens.json", "w").write(json.dumps(tokens, indent=4))

    def is_expired(self, token):
        header, payload, sign = token.split(".")
        payload = b64decode(payload + "==").decode()
        jload = json.loads(payload)
        now = round(datetime.now().timestamp())
        exp = jload['exp']
        if now > exp:
            return True

        return False

    def save_failed_token(self, userid, data):
        file = "auth_failed.json"
        if not os.path.exists(file):
            open(file, "w").write(json.dumps({}))

        acc = json.loads(open(file, 'r').read())
        if str(userid) in acc.keys():
            return

        acc[str(userid)] = data
        open(file, 'w').write(json.dumps(acc, indent=4))

    def load_config(self):
        config = json.loads(open('config.json', 'r').read())
        self.DEFAULT_INTERVAL = config['interval']
        self.MIN_WIN = config['game_point']['low']
        self.MAX_WIN = config['game_point']['high']
        if self.MIN_WIN > self.MAX_WIN:
            self.log(f"{kuning}high value must be higher than lower value")
            sys.exit()


    def countdown(self, t):
        while t:
            menit, detik = divmod(t, 60)
            jam, menit = divmod(menit, 60)
            jam = str(jam).zfill(2)
            menit = str(menit).zfill(2)
            detik = str(detik).zfill(2)
            print(f"{putih}waiting until {jam}:{menit}:{detik} ", flush=True, end="\r")
            t -= 1
            time.sleep(1)
        print("                          ", flush=True, end="\r")

    def main(self):
        banner = f"""
    {hijau}AUTO CLAIM FOR {putih}BLUM {hijau}/ {biru}@BlumCryptoBot
    
    {hijau}By : {putih}t.me/AkasakaID
    {putih}Github : {hijau}@AkasakaID
    
    {hijau}Message : {putih}Dont forget to 'git pull' maybe i update the bot !
        """
        arg = argparse.ArgumentParser()
        arg.add_argument('--marinkitagawa', action="store_true", help="no clear the terminal !")
        arg.add_argument('--data', help="Custom data input (default: data.txt)", default="data.txt")
        arg.add_argument('--autotask', action="store_true", help="enable feature auto complete task !")
        args = arg.parse_args()
        if not args.marinkitagawa:
            os.system("cls" if os.name == "nt" else "clear")

        print(banner)
        if not os.path.exists(args.data):
            self.log(f'{merah}{args.data} not found, please input valid file name !')
            sys.exit()

        datas = open(args.data, "r").read().splitlines()
        self.log(f"{hijau}total account : {putih}{len(datas)}")
        if len(datas) <= 0:
            self.log(f"{merah}add data account in {args.data} first")
            sys.exit()

        self.log(self.garis)
        while True:
            try:
                list_countdown = []
                for no, data in enumerate(datas):
                    try:
                        self.log(f"{hijau}account number - {putih}{no + 1}")
                        data_parse = self.data_parsing(data)
                        user = json.loads(data_parse["user"])
                        chatid = user['id']
                        self.log(f"{hijau}login as : {putih}{user['first_name']}")
                        access_token = self.get_local_token(chatid)
                        failed_fetch_token = False
                        user_id = self.get_user(data, chatid)
                        self.claim_farming(data, user_id)
                        if args.autotask:
                            self.check_tasks(data, user_id, chatid)
                        self.log(self.garis)
                        self.countdown(self.DEFAULT_INTERVAL)
                    except KeyError:
                        print("KeyError: 'request bitcointap json has error")
                time.sleep(3600)        
            except KeyboardInterrupt:
                sys.exit()
            except BaseException as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    try:
        app = BitcoinTap()
        app.load_config()
        app.main()
    except KeyboardInterrupt:
        sys.exit()
