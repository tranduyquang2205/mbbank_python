from mitmproxy import ctx
import json
import os
from datetime import datetime

class MBBankCapture:
    def __init__(self):
        self.captured_requests = []
        self.output_dir = "captured_apis"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def request(self, flow):
        # Chỉ capture các request đến domain của MB Bank
        if "online.mbbank.com.vn" in flow.request.pretty_url:
            request_data = {
                "timestamp": datetime.now().isoformat(),
                "method": flow.request.method,
                "url": flow.request.pretty_url,
                "headers": dict(flow.request.headers),
                "content": flow.request.content.decode('utf-8', 'ignore') if flow.request.content else None
            }
            
            # Lưu request
            self.captured_requests.append(request_data)
            
            # In thông tin request
            ctx.log.info(f"Captured {flow.request.method} request to {flow.request.pretty_url}")
            
            # Lưu vào file nếu là request login
            if "/doLogin" in flow.request.pretty_url:
                filename = f"{self.output_dir}/login_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(request_data, f, indent=2, ensure_ascii=False)
                ctx.log.info(f"Saved login request to {filename}")

    def response(self, flow):
        # Chỉ capture các response từ domain của MB Bank
        if "online.mbbank.com.vn" in flow.request.pretty_url:
            response_data = {
                "timestamp": datetime.now().isoformat(),
                "method": flow.request.method,
                "url": flow.request.pretty_url,
                "status_code": flow.response.status_code,
                "headers": dict(flow.response.headers),
                "content": flow.response.content.decode('utf-8', 'ignore') if flow.response.content else None
            }
            
            # Lưu response
            self.captured_requests.append(response_data)
            
            # In thông tin response
            ctx.log.info(f"Captured response from {flow.request.pretty_url} with status {flow.response.status_code}")
            
            # Lưu vào file nếu là response login
            if "/doLogin" in flow.request.pretty_url:
                filename = f"{self.output_dir}/login_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(response_data, f, indent=2, ensure_ascii=False)
                ctx.log.info(f"Saved login response to {filename}")

addons = [MBBankCapture()] 