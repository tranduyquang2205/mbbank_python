
import requests
import json
import time
class MBBANK:
    def __init__(self):
        self.keyanticaptcha = "b8246038ce1540888c4314a6c043dcae"

    def login(self, username, password, captchaText):
        url = 'https://online.mbbank.com.vn/retail_web/internetbanking/doLogin'
        headers = {
            'Authorization': 'Basic QURNSU46QURNSU4=',
            'Content-Type': 'application/json'
        }
        data = {
            "userId": username,
            "password": password,
            "captcha": captchaText,
            "sessionId": None,
            "refNo": "6fc291182d34a5167e1e9a72c9070531-2021121521221061",
            "deviceIdCommon": "c1gslvi1-0000-0000-0000-2021121518290580"
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.text

    def re_login(self, myUser, row):
        generateImei = self.generateImei()
        login_check = self.handleLogin(row["username"], row["password"])
        login_check = json.loads(login_check)
        if login_check['result']['message'] != 'OK' or not login_check['result']['ok'] or login_check['result']['responseCode'] != '00':
            return False
        else:
            is_exist = self.get_row("SELECT * FROM `account_mbbank` WHERE `username` = '" + row["username"] + "' ")
            if is_exist:
                create = self.update("account_mbbank", {
                    'user_id': myUser['id'],
                    'name': login_check['cust']['nm'],
                    'username': row["username"],
                    'password': row["password"],
                    'account': login_check['cust']['chrgAcctCd'],
                    'sessionId': login_check['sessionId'],
                    'json': json.dumps(login_check),
                    'deviceId': generateImei,
                    'token': self.CreateToken(),
                    'status': 'success',
                    'TimeLogin': time()
                }, "`username` = '" + row["username"] + "'")
            else:
                create = self.insert("account_mbbank", {
                    'user_id': myUser['id'],
                    'name': login_check['cust']['nm'],
                    'username': row["username"],
                    'password': row["password"],
                    'account': login_check['cust']['chrgAcctCd'],
                    'sessionId': login_check['sessionId'],
                    'deviceId': generateImei,
                    'token': self.CreateToken(),
                    'status': 'success',
                    'json': json.dumps(login_check),
                    'TimeLogin': time()
                })
            if create:
                return login_check
            else:
                return False

    def get_balance(self, session,account_number):
        url = 'https://online.mbbank.com.vn/api/retail-web-accountms/getBalance'
        headers = {
            'Authorization': 'Basic QURNSU46QURNSU4=',
            'Content-Type': 'application/json'
        }
        data = {
            "sessionId": session["sessionId"],
            "refNo": session["refNo"],
            "deviceIdCommon": session["cust"]["deviceId"]
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        data = json.loads(response.text)
        
        # Search for the account in "acct_list"
        for acct in data.get("acct_list", []):
            if acct.get("acctNo") == account_number:
                return acct.get("currentBalance")
        return "-1"
    def createTaskCaptcha1(self, base64_img):
            url = "https://api.anti-captcha.com/createTask"
            payload = json.dumps({
            "clientKey": "f3a44e66302c61ffec07c80f4732baf3",
            "task": {
                "type": "ImageToTextTask",
                "body": base64_img,
                "phrase": False,
                "case": False,
                "numeric": 0,
                "math": False,
                "minLength": 0,
                "maxLength": 0
            },
            "softId": 0
            })
            headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)
            return(response.text)
    def createTaskCaptcha(self, base64_img):
        url = 'http://103.72.96.214:8277/api/captcha/mbbank'
        payload = json.dumps({
        "base64": base64_img
        })
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=payload)
        return response.text

    def checkProgressCaptcha(self, task_id):
        url = 'https://api.anti-captcha.com/getTaskResult'
        data = {
            "clientKey": "f3a44e66302c61ffec07c80f4732baf3",
            "taskId": task_id
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_json = json.loads(response.text)
        if response_json["status"] != "ready":
            time.sleep(1)
            return self.checkProgressCaptcha(task_id)
        else:
            return response_json["solution"]["text"]

    def getCaptcha(self):
        url = 'https://online.mbbank.com.vn/retail-web-internetbankingms/getCaptchaImage'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic QURNSU46QURNSU4='
        }
        data = {
            "refNo": "2021121519165529",
            "deviceIdCommon": "c1gslvi1-0000-0000-0000-2021121518290580",
            "sessionId": ""
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_json = json.loads(response.text)
        return response_json["imageString"]

    def getTransactionHistory(self, fromDate,toDate, session):
        url = 'https://online.mbbank.com.vn/api/retail-transactionms/transactionms/get-account-transaction-history'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic QURNSU46QURNSU4=',
            'RefNo': session["refNo"],
            'Deviceid': session["cust"]["deviceId"],
            'X-Request-Id': session["refNo"],
        }
        data = {
            "accountNo": session["cust"]["chrgAcctCd"],
            "fromDate": fromDate,
            "toDate": toDate,
            "sessionId": session["sessionId"],
            "refNo": session["refNo"],
            "deviceIdCommon": session["cust"]["deviceId"]
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.text

    def handleGetTransactionHistory(self, data):
        self.insertToDB(data)
        data_raw = json.dumps(data)
        print(data_raw)
        new_data = self.build_saveData(data)
        with open("./data.json", "w") as f:
            json.dump(new_data, f)

    def insertToDB(self, data):
        for value in data["transactionHistoryList"]:
            description = value["description"].lower()
            if "tbolach5" in description:
                username = description.split('tbolach5 ')[1]
                money = value["creditAmount"]
                time_exchange = value["transactionDate"]
                print(f"{username}-{money}-{time_exchange}")

    def build_saveData(self, data):
        new_data = {}
        new_data["status"] = "done"
        new_data["last_excute"] = int(time.time())
        new_data["data"] = data
        return new_data

    def handleLogin(self, username, password):
        base64_captcha_img = self.getCaptcha()
        task = self.createTaskCaptcha(base64_captcha_img)
        captchaText =json.loads(task)['captcha']
        # task = self.createTaskCaptcha1(base64_captcha_img)
        # captchaText = self.checkProgressCaptcha(json.loads(task)['taskId'])
        session_raw = self.login(username, password, captchaText)
        
        return session_raw
        

        