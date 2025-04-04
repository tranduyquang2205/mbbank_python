from flask import Flask, request, jsonify
import hashlib
import time
import random
import string

app = Flask(__name__)

# Simulated user database
USERS = {
    "test_user": {
        "password": hashlib.md5("test123".encode()).hexdigest(),
        "account_number": "1234567890"
    }
}

def generate_session_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

@app.route('/api/retail_web/internetbanking/v2.0/doLogin', methods=['POST'])
def login():
    try:
        # Get encrypted data from request
        data = request.get_json()
        
        # Simulate decryption (in real implementation, this would decrypt the data)
        user_id = data.get('userId')
        password = data.get('password')
        captcha = data.get('captcha')
        device_id = data.get('deviceIdCommon')
        
        # Check if user exists
        if user_id not in USERS:
            return jsonify({
                'result': {
                    'responseCode': '01',
                    'message': 'Invalid username or password'
                }
            }), 401
            
        # Verify password
        if password != USERS[user_id]['password']:
            return jsonify({
                'result': {
                    'responseCode': '01',
                    'message': 'Invalid username or password'
                }
            }), 401
            
        # Verify captcha (simplified)
        if captcha != "1111":
            return jsonify({
                'result': {
                    'responseCode': '02',
                    'message': 'Invalid captcha'
                }
            }), 400
            
        # Generate session data
        session_id = generate_session_id()
        
        # Simulate successful login
        return jsonify({
            'result': {
                'responseCode': '00',
                'message': 'Success',
                'sessionId': session_id,
                'defaultAccount': USERS[user_id]['account_number'],
                'cust': {
                    'name': 'Test User',
                    'cif': '12345678',
                    'mobile': '0123456789'
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'result': {
                'responseCode': '99',
                'message': str(e)
            }
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc') 