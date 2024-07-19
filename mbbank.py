
import requests
import json
import time
import os
import hashlib
from datetime import datetime

class MBBANK:
    def __init__(self,username, password, account_number):
        self.password = password
        self.username = username
        self.account_number = account_number
        self.is_login = False
        self.file = f"data/{username}.txt"
        self.device_id = self.generate_device_id()
        self.session = requests.Session()
        
        if not os.path.exists(self.file):
                    self.username = username
                    self.password = password
                    self.account_number = account_number
                    self.sessionId = ""
                    self.mobileId = ""
                    self.clientId = ""
                    self.cif = ""
                    self.res = ""
                    self.browserToken = ""
                    self.browserId = ""
                    self.E = ""
                    self.tranId = ""
                    self.refNo = ""
                    self.browserId = hashlib.md5(self.username.encode()).hexdigest()
                    self.save_data()
                    
        else:
            self.parse_data()
            self.username = username
            self.password = password
            self.account_number = account_number
    def save_data(self):
        data = {
            'username': self.username,
            'password': self.password,
            'account_number': self.account_number,
            'sessionId': getattr(self, 'sessionId', ''),
            'mobileId': getattr(self, 'mobileId', ''),
            'clientId': self.clientId,
            'cif': getattr(self, 'cif', ''),
            'E': getattr(self, 'E', ''),
            'res': getattr(self, 'res', ''),
            'tranId': getattr(self, 'tranId', ''),
            'browserToken': getattr(self, 'browserToken', ''),
            'browserId': self.browserId,
            'refNo': self.refNo,
        }
        with open(self.file, 'w') as f:
            json.dump(data, f)

    def parse_data(self):
        with open(self.file, 'r') as f:
            data = json.load(f)
        self.username = data.get('username', '')
        self.password = data.get('password', '')
        self.account_number = data.get('account_number', '')
        self.sessionId = data.get('sessionId', '')
        self.mobileId = data.get('mobileId', '')
        self.clientId = data.get('clientId', '')
        self.token = data.get('token', '')
        self.accessToken = data.get('accessToken', '')
        self.authToken = data.get('authToken', '')
        self.cif = data.get('cif', '')
        self.res = data.get('res', '')
        self.tranId = data.get('tranId', '')
        self.browserToken = data.get('browserToken', '')
        self.browserId = data.get('browserId', '')
        self.E = data.get('E', '')
        self.refNo = data.get('refNo', '')
        
    def login(self, captchaText):
        url = 'https://online.mbbank.com.vn/api/retail_web/internetbanking/v2.0/doLogin'
        headers = {
            'Cache-Control': 'no-cache',
            'Accept': 'application/json, text/plain, */*',
            'Authorization': 'Basic RU1CUkVUQUlMV0VCOlNEMjM0ZGZnMzQlI0BGR0AzNHNmc2RmNDU4NDNm',
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Origin": "https://online.mbbank.com.vn",
            "Referer": "https://online.mbbank.com.vn/",
            "Content-Type": "application/json; charset=UTF-8",
            'app': "MB_WEB",
        }
        param = {
            "userId": self.username,
            "password": hashlib.md5(self.password.encode()).hexdigest(),
            "captcha": captchaText,
            "ibAuthen2faString": "c7a1beebb9400375bb187daa33de9659",
            "sessionId": None,
            "refNo": self.get_time_now(),
            "deviceIdCommon": self.device_id,
        }
        request_data = self.encrypt_data(param)
        # print(request_data)
        
        result = self.curlPost(url, headers=headers, data=(request_data))
        
        if 'result' in result and 'responseCode' in result['result'] and result['result']['responseCode'] == "00":
            self.sessionId = result
            self.save_data()
            self.is_login = True
            return {
                'code': 200,
                'success': True,
                'message': "success",
                'sessionId': self.sessionId,
            }
        else:
            return {
                'code': 500,
                'success': False,
                'message': result['result']['message'] if  'result' in result and 'message' in result['result'] else result,
                "param": param,
                'data': result if result else ""
            }
    def curlPost(self, url, data,headers = None):
            if not headers:
                headers = {
                'Cache-Control': 'no-cache',
                'Accept': 'application/json, text/plain, */*',
                'Authorization': 'Basic RU1CUkVUQUlMV0VCOlNEMjM0ZGZnMzQlI0BGR0AzNHNmc2RmNDU4NDNm',
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                "Origin": "https://online.mbbank.com.vn",
                "Referer": "https://online.mbbank.com.vn/",
                "Content-Type": "application/json; charset=UTF-8",
                'app': "MB_WEB",
                }
            response = self.session.post(url, headers=headers, data=json.dumps(data))
            try:
                result = response.json()
            except:
                result = response.text
            return result
    def encrypt_data(self,data):
        url = "https://mbcrypt.pay2world.vip/encrypt"
        payload = json.dumps(data)
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        try:
            return response.json()
        except:
            return response.text
        
    def generate_device_id(self):
        return "s1rmi184-mbib-0000-0000-" + self.get_time_now()
    def get_time_now(self):
        return datetime.now().strftime("%Y%m%d%H%M%S") 

    def get_balance(self):
        if not self.is_login:
            login = self.handleLogin()
            if not login['success']:
                return login
        url = 'https://online.mbbank.com.vn/api/retail-web-accountms/getBalance'
        headers = {
            'Authorization': 'Basic RU1CUkVUQUlMV0VCOlNEMjM0ZGZnMzQlI0BGR0AzNHNmc2RmNDU4NDNm',
            'Content-Type': 'application/json'
        }
        data = {
            "sessionId": self.sessionId["sessionId"],
            "refNo": self.sessionId["refNo"],
            "deviceIdCommon": self.sessionId["cust"]["deviceId"]
        }
        response = self.curlPost(url, headers=headers, data=data)
        if 'result' in response and 'responseCode' in response['result'] and response['result']['responseCode'] == "00":
            for account in response['acct_list']:
                if self.account_number == account['acctNo']:
                    if float(account['currentBalance']) < 0 :
                        return {'code':448,'success': False, 'message': 'Blocked account with negative balances!',
                                'data': {
                                    'balance':float(account['currentBalance'])
                                }
                                }
                    else:
                        return {'code':200,'success': True, 'message': 'Thành công',
                                'data':{
                                    'account_number':self.account_number,
                                    'balance':float(account['currentBalance'])
                        }}
            return {'code':404,'success': False, 'message': 'account_number not found!'} 
        else: 
            return {'code':520 ,'success': False, 'message': 'Unknown Error!'} 
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
        url = 'https://online.mbbank.com.vn/api/retail-web-internetbankingms/getCaptchaImage'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic RU1CUkVUQUlMV0VCOlNEMjM0ZGZnMzQlI0BGR0AzNHNmc2RmNDU4NDNm'
        }
        data = {
            "refNo": self.get_time_now(),
            "deviceIdCommon": self.device_id,
            "sessionId": ""
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_json = json.loads(response.text)
        return response_json["imageString"]

    def getTransactionHistory(self, fromDate,toDate,account_number):
        if not self.is_login:
            login = self.handleLogin()
            if not login['success']:
                return login
        url = 'https://online.mbbank.com.vn/api/retail-transactionms/transactionms/get-account-transaction-history'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic RU1CUkVUQUlMV0VCOlNEMjM0ZGZnMzQlI0BGR0AzNHNmc2RmNDU4NDNm',
            'RefNo': self.sessionId["refNo"],
            'Deviceid': self.sessionId["cust"]["deviceId"],
            'X-Request-Id': self.sessionId["refNo"],
        }
        data = {
            "accountNo": account_number,
            "fromDate": fromDate,
            "toDate": toDate,
            "sessionId": self.sessionId["sessionId"],
            "refNo": self.sessionId["refNo"],
            "deviceIdCommon": self.sessionId["cust"]["deviceId"]
        }
        print(data)
        response = self.curlPost(url, headers=headers, data=data)
        print(response)
        if 'result' in response and 'responseCode' in response['result'] and response['result']['responseCode'] == "00":
            return {'code':200,'success': True, 'message': 'Thành công',
                            'data':{
                                'transactions':response['transactionHistoryList'],
                    }}
        else:
            return  {
                    "success": False,
                    "code": 503,
                    "param":data,
                    "message": "Service Unavailable!"
                }

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

    def handleLogin(self):
        base64_captcha_img = self.getCaptcha()
        task = self.createTaskCaptcha(base64_captcha_img)
        captchaText =json.loads(task)['captcha']
        # task = self.createTaskCaptcha1(base64_captcha_img)
        # captchaText = self.checkProgressCaptcha(json.loads(task)['taskId'])
        session_raw = self.login(captchaText)
        
        
        return session_raw
        

