
import requests
import json
import time
import os
import hashlib
from datetime import datetime
import random
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES,PKCS1_v1_5,PKCS1_OAEP
from Cryptodome.Random import get_random_bytes
import base64
import string
from Cryptodome.Util import Counter
from bypass_ssl_v3 import get_legacy_session
from urllib.parse import quote
import socket
import urllib
import ssl
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session_requests = get_legacy_session()

class MBBANK:
    def __init__(self,username, password, account_number,adb_device_id=None,smart_otp_pin=None, proxy_list=None):
        self.proxy_list = proxy_list
        if self.proxy_list:
            self.proxy_info = self.proxy_list.pop(0)
            proxy_host, proxy_port, username_proxy, password_proxy = self.proxy_info.split(':')
            self.proxies = {
                'http': f'socks5://{username_proxy}:{password_proxy}@{proxy_host}:{proxy_port}',
                'https': f'socks5://{username_proxy}:{password_proxy}@{proxy_host}:{proxy_port}'
            }
        else:
            self.proxies = None
        
        self.password = password
        self.username = username
        self.account_number = account_number
        self.adb_device_id=adb_device_id
        self.smart_otp_pin=smart_otp_pin
        self.is_login = False
        self.file = f"db/users/{username}.txt"
        self.device_id = self.generate_device_id()
        self.session = requests.Session()
        
        if not os.path.exists(self.file):
                    self.username = username
                    self.password = password
                    self.account_number = account_number
                    self.adb_device_id = adb_device_id
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
                    self.is_login = False
                    self.time_login = time.time()
                    self.browserId = hashlib.md5(self.username.encode()).hexdigest()
                    self.save_data()
                    
        else:
            self.parse_data()
            self.username = username
            self.password = password
            self.account_number = account_number
            self.adb_device_id = adb_device_id
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
            'is_login':self.is_login,
            'time_login': self.time_login,
            'adb_device_id': self.adb_device_id,
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
        self.is_login = data['is_login']
        self.time_login = data['time_login']
        self.adb_device_id = data['adb_device_id']
        
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
            "refNo": self.generate_ref_no(),
            "deviceIdCommon": self.device_id,
        }
        print(param)
        request_data = self.encrypt_data(param)
        print(request_data)
        
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
            response = self.session.post(url, headers=headers, data=json.dumps(data), proxies=self.proxies, verify=False)
            try:
                result = response.json()
            except:
                result = response.text
            return result
    def encrypt_data(self,data):
        url = "https://mbcrypt1.pay2world.vip/encrypt"
        payload = json.dumps(data)
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload, proxies=self.proxies, verify=False)

        try:
            return response.json()
        except:
            return response.text
        
    def generate_device_id(self):
        return "s1rmi184-mbib-0000-0000-" + self.get_time_now()
    def get_time_now(self):
        return datetime.now().strftime("%Y%m%d%H%M%S") 
    
    def generate_ref_no(self):
        return self.username +'-'+ self.get_time_now()+'-'+ str(random.randint(10000, 99999))

    def get_balance(self):
        if not self.is_login or time.time() - self.time_login > 900:
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
    def createTaskCaptcha(self, base64_img):
        url = 'http://103.72.96.214:8277/api/captcha/mbbank'
        payload = json.dumps({
        "base64": base64_img
        })
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=payload, proxies=self.proxies, verify=False)
        return response.text

    def getCaptcha(self):
        url = 'https://online.mbbank.com.vn/api/retail-web-internetbankingms/getCaptchaImage'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic RU1CUkVUQUlMV0VCOlNEMjM0ZGZnMzQlI0BGR0AzNHNmc2RmNDU4NDNm'
        }
        data = {
            "refNo": self.generate_ref_no(),
            "deviceIdCommon": self.device_id,
            "sessionId": ""
        }
        response = requests.post(url, headers=headers, data=json.dumps(data), proxies=self.proxies, verify=False)
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
    def handleLogin(self):
        base64_captcha_img = self.getCaptcha()
        task = self.createTaskCaptcha(base64_captcha_img)
        captchaText =json.loads(task)['captcha']
        session_raw = self.login(captchaText)
        return session_raw
    
    def get_bank_name(self,ben_account_number, bank_code):
        if not self.is_login or time.time() - self.time_login > 900:
            login = self.handleLogin()
            if not login['success']:
                return login

        url = 'https://online.mbbank.com.vn/api/retail_web/transfer/inquiryAccountName'
        headers = {
            'Authorization': 'Basic RU1CUkVUQUlMV0VCOlNEMjM0ZGZnMzQlI0BGR0AzNHNmc2RmNDU4NDNm',
            'Content-Type': 'application/json'
        }
        data = {
            "bankCode": bank_code,
            "creditAccount": ben_account_number,
            "creditAccountType": "ACCOUNT",
            "debitAccount": self.account_number,
            "deviceIdCommon": self.device_id,
            "refNo": self.refNo,
            "remark": "",
            "sessionId": self.sessionId["sessionId"],
            "type": "FAST"
        }
        response = self.curlPost(url, headers=headers, data=data)
        if 'result' in response and 'responseCode' in response['result'] and response['result']['responseCode'] == "00" and 'benName' in response:
            return response['benName']
        else:
            return None
    def verify_make_transfer(self,bank_send, to_account, amount, description,account_name,logger):
        if not self.is_login or time.time() - self.time_login > 900:
            login = self.handleLogin()
            if not login['success']:
                return login

        url = 'https://online.mbbank.com.vn/api/retail_web/transfer/verifyMakeTransfer'
        headers = {
            'Authorization': 'Basic RU1CUkVUQUlMV0VCOlNEMjM0ZGZnMzQlI0BGR0AzNHNmc2RmNDU4NDNm',
            'Content-Type': 'application/json'
        }
        data = {
            "amount": amount,
            "benAccountName": account_name,
            "benAccountNumber": to_account,
            "benBankCd": bank_send['bankCode'],
            "destType": "ACCOUNT",
            "deviceIdCommon": self.device_id,
            "message": description,
            "refNo": self.refNo,
            "sessionId": self.sessionId["sessionId"],
            "srcAccountNumber": self.account_number,
            "transferType": "FAST"
        }
        data = self.encrypt_data(data)
        response = self.curlPost(url, headers=headers, data=data)
        if 'result' in response and 'responseCode' in response['result'] and response['result']['responseCode'] == "00" and 'benName' in response:
            return response['benName']
        else:
            return None
    def verify_make_transfer(self,bank_send, to_account, amount, description,account_name,logger):
        if not self.is_login or time.time() - self.time_login > 900:
            login = self.handleLogin()
            if not login['success']:
                return login

        url = 'https://online.mbbank.com.vn/api/retail_web/transfer/verifyMakeTransfer'
        headers = {
            'Authorization': 'Basic RU1CUkVUQUlMV0VCOlNEMjM0ZGZnMzQlI0BGR0AzNHNmc2RmNDU4NDNm',
            'Content-Type': 'application/json'
        }
        data = {
            "amount": amount,
            "benAccountName": account_name,
            "benAccountNumber": to_account,
            "benBankCd": bank_send['bankCode'],
            "destType": "ACCOUNT",
            "deviceIdCommon": self.device_id,
            "message": description,
            "refNo": self.refNo,
            "sessionId": self.sessionId["sessionId"],
            "srcAccountNumber": self.account_number,
            "transferType": "FAST"
        }
        data = self.encrypt_data(data)
        response = self.curlPost(url, headers=headers, data=data)
        if 'result' in response and 'responseCode' in response['result'] and response['result']['responseCode'] == "00" and 'benName' in response:
            return response['benName']
        else:
            return None

