import json
import urllib.parse
from curl_cffi import requests
from core import logger
logger.install()
from core import cookies_manager

cookies = cookies_manager.load_cookies("cookies1.txt")
token = cookies.get('session_token', '')

def scrub(s):
    return s.replace(token, "<TOK>") if token else s

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'

# Одна сессия: сперва зайдём на homepage, чтобы получить свежий XSRF-TOKEN (если выдаётся).
s = requests.Session(impersonate="chrome120")
s.cookies.update(cookies)
s.headers.update({'User-Agent': UA, 'Accept': 'text/html,*/*', 'Accept-Language': 'en-US,en;q=0.9'})

r0 = s.get('https://kick.com/', timeout=15)
print("homepage:", r0.status_code)

# Смотрим, появился ли XSRF-TOKEN среди cookies сессии (имена только).
names = sorted(c.name for c in s.cookies.jar)
print("session cookie names now:", names)
xsrf = None
for c in s.cookies.jar:
    if c.name.upper() == 'XSRF-TOKEN':
        xsrf = urllib.parse.unquote(c.value)
print("has XSRF-TOKEN:", bool(xsrf))

api_headers = {
    'User-Agent': UA,
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Authorization': f'Bearer {token}',
    'X-Client-Token': 'e1393935a959b4020a4491574f6490129f678acdaa92760471263db43487f823',
    'Referer': 'https://kick.com/',
    'Origin': 'https://kick.com',
    'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-site',
}
if xsrf:
    api_headers['X-XSRF-TOKEN'] = xsrf

for url in ('https://kick.com/api/v1/user',
            'https://web.kick.com/api/v1/channels/me'):
    r = s.get(url, headers=api_headers, timeout=10)
    print(f"{r.status_code} {url} (len {len(r.text)})")
    print("   ->", scrub(r.text)[:200].strip())

s.close()
