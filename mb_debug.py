from mitmproxy import ctx
import json
import os
from datetime import datetime
import re
import jsbeautifier
from urllib.parse import urlparse, parse_qs

class MBBankDebug:
    def __init__(self):
        self.captured_requests = []
        self.output_dir = "debug_data"
        self.js_files = {}
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            os.makedirs(f"{self.output_dir}/js")
            os.makedirs(f"{self.output_dir}/api")

    def save_debug_info(self, data, prefix, suffix=""):
        filename = f"{self.output_dir}/{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{suffix}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filename

    def analyze_js(self, content, url):
        # Tìm các hàm mã hóa
        encryption_patterns = [
            r'function\s+encrypt\s*\([^)]*\)\s*{.*?}',
            r'function\s+decrypt\s*\([^)]*\)\s*{.*?}',
            r'crypto\.',
            r'encryption',
            r'hash',
            r'sha256',
            r'md5'
        ]
        
        # Đẹp hóa code JavaScript
        beautified = jsbeautifier.beautify(content)
        
        # Lưu file JS gốc
        js_filename = f"{self.output_dir}/js/{datetime.now().strftime('%Y%m%d_%H%M%S')}.js"
        with open(js_filename, 'w', encoding='utf-8') as f:
            f.write(beautified)
            
        # Tìm các pattern mã hóa
        found_patterns = []
        for pattern in encryption_patterns:
            matches = re.finditer(pattern, beautified, re.DOTALL | re.IGNORECASE)
            for match in matches:
                found_patterns.append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'line_number': beautified[:match.start()].count('\n') + 1
                })
                
        return {
            'url': url,
            'saved_file': js_filename,
            'encryption_patterns': found_patterns
        }

    def request(self, flow):
        if "online.mbbank.com.vn" in flow.request.pretty_url:
            # Parse URL để lấy thông tin
            parsed_url = urlparse(flow.request.pretty_url)
            path = parsed_url.path
            query = parse_qs(parsed_url.query)
            
            request_data = {
                "timestamp": datetime.now().isoformat(),
                "method": flow.request.method,
                "url": flow.request.pretty_url,
                "path": path,
                "query_params": query,
                "headers": dict(flow.request.headers),
                "content": flow.request.content.decode('utf-8', 'ignore') if flow.request.content else None
            }
            
            # Phân tích JavaScript nếu là file .js
            if path.endswith('.js'):
                js_analysis = self.analyze_js(
                    flow.request.content.decode('utf-8', 'ignore'),
                    flow.request.pretty_url
                )
                request_data['js_analysis'] = js_analysis
            
            # Lưu request
            self.captured_requests.append(request_data)
            
            # In thông tin debug
            ctx.log.info(f"[DEBUG] {flow.request.method} {flow.request.pretty_url}")
            if 'js_analysis' in request_data:
                ctx.log.info(f"[JS] Found {len(request_data['js_analysis']['encryption_patterns'])} encryption patterns")
            
            # Lưu vào file nếu là request quan trọng
            if any(keyword in flow.request.pretty_url for keyword in ['/doLogin', '/init', '/captcha', '/challenge']):
                filename = self.save_debug_info(request_data, 'request')
                ctx.log.info(f"[SAVED] Request saved to {filename}")

    def response(self, flow):
        if "online.mbbank.com.vn" in flow.request.pretty_url:
            response_data = {
                "timestamp": datetime.now().isoformat(),
                "method": flow.request.method,
                "url": flow.request.pretty_url,
                "status_code": flow.response.status_code,
                "headers": dict(flow.response.headers),
                "content": flow.response.content.decode('utf-8', 'ignore') if flow.response.content else None
            }
            
            # Phân tích response
            try:
                if flow.response.headers.get('content-type', '').startswith('application/json'):
                    response_data['parsed_json'] = json.loads(response_data['content'])
            except:
                pass
                
            # Lưu response
            self.captured_requests.append(response_data)
            
            # In thông tin debug
            ctx.log.info(f"[DEBUG] Response from {flow.request.pretty_url} - Status: {flow.response.status_code}")
            
            # Lưu vào file nếu là response quan trọng
            if any(keyword in flow.request.pretty_url for keyword in ['/doLogin', '/init', '/captcha', '/challenge']):
                filename = self.save_debug_info(response_data, 'response')
                ctx.log.info(f"[SAVED] Response saved to {filename}")

addons = [MBBankDebug()] 