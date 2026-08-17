import json
from curl_cffi import requests
from core import logger
logger.install()
from core import cookies_manager

cookies = cookies_manager.load_cookies("cookies1.txt")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'ru-RU,ru;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Authorization': f"Bearer {cookies.get('session_token')}",
    'X-Client-Token': 'e1393935a959b4020a4491574f6490129f678acdaa92760471263db43487f823',
    'Referer': 'https://kick.com/',
    'Origin': 'https://kick.com',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Ch-Ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Priority': 'u=1, i',
}

CANDIDATES = [
    'https://web.kick.com/api/v1/user',
    'https://kick.com/api/v1/user',
    'https://web.kick.com/api/v2/user',
    'https://kick.com/api/v2/user',
]

def find_name(d, depth=0):
    """Ищем правдоподобный ник в JSON, печатаем ключи верхнего уровня."""
    if isinstance(d, dict):
        for k in ('username', 'slug', 'name'):
            v = d.get(k)
            if isinstance(v, str) and v.strip():
                return f"{k}={v.strip()!r}"
        # заглянем на уровень вглубь
        for key in ('data', 'user', 'streamer_channel'):
            inner = d.get(key)
            r = find_name(inner, depth + 1)
            if r:
                return f"{key}.{r}"
    return None

for url in CANDIDATES:
    s = requests.Session(impersonate="chrome120")
    s.cookies.update(cookies)
    s.headers.update(HEADERS)
    try:
        r = s.get(url, timeout=10)
        try:
            j = r.json()
            keys = list(j.keys()) if isinstance(j, dict) else type(j).__name__
        except Exception:
            j, keys = None, "(not json)"
        name = find_name(j) if j is not None else None
        print(f"{r.status_code}  {url}")
        print(f"      top-keys: {keys}")
        print(f"      name:     {name}")
    except Exception as e:
        print(f"ERR {url}: {e}")
    finally:
        s.close()
