import os
import sys
import io
import json
import shutil
import threading
import contextlib

# --- Подготовка: два фейковых аккаунта в Netscape-формате ---
NETSCAPE = (
    "# Netscape HTTP Cookie File\n"
    ".kick.com\tTRUE\t/\tTRUE\t0\tsession_token\tFAKE_TOKEN_123\n"
)
for n in (1, 2):
    with open(f"cookies{n}.txt", "w", encoding="utf-8") as f:
        f.write(NETSCAPE)

import index
from core import kick, view_controller, cookies_manager, logger

results = {}

# 1) Обнаружение аккаунтов
accts = index.discover_accounts()
results["discovered"] = [a["slot"] for a in accts]
assert results["discovered"] == [1, 2], results["discovered"]

# 2) Загрузка cookies действительно парсит session_token
c = cookies_manager.load_cookies("cookies1.txt")
results["cookie_token"] = (c or {}).get("session_token")
assert results["cookie_token"] == "FAKE_TOKEN_123", c

# 3) Создание файлов прогресса из шаблона (форма get_all_campaigns: {'data': [...]})
template = {"data": []}
index.ensure_progress_files(accts, template)
results["views_created"] = [
    os.path.exists("views/cookies1.json"),
    os.path.exists("views/cookies2.json"),
]
assert all(results["views_created"]), results["views_created"]
# файлы содержат валидный пустой шаблон
with open("views/cookies1.json", encoding="utf-8") as f:
    j = json.load(f)
assert j["data"]["planned"] == [], j

# --- Стабы, чтобы не ходить в сеть и не крутить бесконечный фарм ---
def fake_nick(cookies, max_attempts=2):
    # cookies1 -> фолбэк (None), cookies2 -> ник с Kick
    return None if cookies.get("session_token") == "FAKE_TOKEN_123_C1" else "CoolNick"

# различаем аккаунты по токену: сделаем токены разными
with open("cookies2.txt", "w", encoding="utf-8") as f:
    f.write(NETSCAPE.replace("FAKE_TOKEN_123", "TOKEN_C2"))
with open("cookies1.txt", "w", encoding="utf-8") as f:
    f.write(NETSCAPE.replace("FAKE_TOKEN_123", "FAKE_TOKEN_123_C1"))

kick.get_account_username = fake_nick

async def fake_check(cookies_file, progress_file):
    return None
view_controller.check_campaigns_claim_status = fake_check

async def fake_streamer_loop(cookies_file, progress_file):
    # один print, затем выход — имитируем работу без бесконечного цикла
    print("farming tick")
index.start_streamer_drops = fake_streamer_loop

# 4) Запускаем реальный путь run_account в потоках и ловим префиксы логов
buf = io.StringIO()
accts2 = index.discover_accounts()
with contextlib.redirect_stdout(buf):
    threads = []
    for acc in accts2:
        t = threading.Thread(target=index._thread_entry, args=(acc, "1"),
                             name=acc["fallback_label"], daemon=True)
        t.start()
        threads.append(t)
    for t in threads:
        t.join(timeout=15)

out = buf.getvalue()

# Проверяем, что строки farming tick помечены ником/фолбэком
results["has_cookies1_prefix"] = "[cookies1] farming tick" in out
results["has_coolnick_prefix"] = "[CoolNick] farming tick" in out
assert results["has_cookies1_prefix"], "no [cookies1] prefix in:\n" + out
assert results["has_coolnick_prefix"], "no [CoolNick] prefix in:\n" + out

print("SMOKE_RESULTS:", json.dumps(results, ensure_ascii=False))
print("ALL_WIRING_OK")
