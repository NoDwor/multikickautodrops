import asyncio
import json
import os
import threading
import traceback
from functools import partial

# ВАЖНО: подменяем print на версию с префиксом [ник] ДО импорта остальных
# модулей, чтобы все существующие print автоматически получали метку аккаунта.
from core import logger
logger.install()

from core import tl
from core import kick
from core import view_controller
from core import formatter
from core import cookies_manager


# Сколько слотов аккаунтов сканируем: cookies1.txt … cookies22.txt
MAX_ACCOUNTS = 22
# Категория (game_id) для фарма — как в исходной программе (13).
CATEGORY_ID = 13
# Папка с файлами прогресса по аккаунтам (views/cookiesN.json).
VIEWS_DIR = "views"


def discover_accounts():
    """Ищем существующие файлы cookies1.txt..cookies22.txt в корне проекта.
    Для каждого найденного собираем описание аккаунта (слот привязан к номеру
    файла, чтобы прогресс не путался между аккаунтами)."""
    accounts = []
    for i in range(1, MAX_ACCOUNTS + 1):
        cookies_file = f"cookies{i}.txt"
        if os.path.exists(cookies_file):
            accounts.append({
                "slot": i,
                "cookies_file": cookies_file,
                "progress_file": os.path.join(VIEWS_DIR, f"cookies{i}.json"),
                "fallback_label": f"cookies{i}",
            })
    return accounts


def choose_mode():
    """Меню режима — спрашиваем один раз, применяем ко всем аккаунтам."""
    menu_items = {
        "1": tl.c["start_streamers_drops"],
        "2": tl.c["start_general_drops"],
        "0": tl.c["exit"],
    }
    while True:
        for key, label in menu_items.items():
            print(f"{key}. {label}")
        choice = input(tl.c["select_menu"]).strip()
        if choice in menu_items:
            return choice
        print(f"\n{tl.c['wrong_choice']}")


def build_template():
    """Один запрос кампаний на всех — используется как шаблон прогресса."""
    try:
        return kick.get_all_campaigns()
    except Exception as e:
        print(tl.c["error_viewing"].format(e=e))
        return None


def ensure_progress_files(accounts, template):
    """Создаём views/cookiesN.json для тех аккаунтов, у кого его ещё нет
    (сохраняет прогресс между перезапусками). Используем общий шаблон."""
    os.makedirs(VIEWS_DIR, exist_ok=True)
    for acc in accounts:
        if os.path.exists(acc["progress_file"]):
            continue
        if isinstance(template, dict) and "data" in template:
            formatter.convert_drops_json(template, filepath=acc["progress_file"])
        else:
            # Запасной пустой шаблон, чтобы аккаунт не падал при отсутствии сети.
            with open(acc["progress_file"], "w", encoding="utf-8") as f:
                json.dump({"data": {"planned": [], "finished": []}}, f,
                          ensure_ascii=False, indent=4)


async def start_general_drops(cookies_file, progress_file):
    while True:
        print(f"\n{tl.c['search_streamers']}")

        try:
            # Получаем случайного стримера из категории
            rndstreamercategory = kick.get_random_stream_from_category(CATEGORY_ID)

            if not rndstreamercategory:
                print(f"\n{tl.c['unablefindstreamer']}")
                print(f"\n{tl.c['waitcd300seconds']}")
                await asyncio.sleep(300)
                continue

            username = rndstreamercategory["username"]
            remaining = await formatter.get_remaining_time(username, json_filename=progress_file)
            print(tl.c["streamer_found"].format(username=username))
            stream_info = await kick.get_stream_info(username)

            if not stream_info["is_live"]:
                print(tl.c["streamer_offline_looking_another"].format(username=username))
                await asyncio.sleep(30)
                continue

            # Проверяем категорию игры
            if stream_info["game_id"] != CATEGORY_ID:
                print(tl.c["streamer_play_another_game"].format(username=username))
                await asyncio.sleep(30)
                continue

            print(tl.c["streamer_online"].format(username=username))
            print(tl.c["starting_view_streamer"].format(remaining=remaining))

            # Запускаем просмотр стрима
            stream_ended = await view_controller.run_with_timer(
                partial(view_controller.view_stream, username, CATEGORY_ID, cookies_file, progress_file),
                remaining + 120
            )

            # Если стрим закончился или сменилась игра
            if stream_ended:
                print(tl.c["streamer_play_another_game"].format(username=username))
                print(f"\n{tl.c['wait_for_new_streamer']}")
                # check drops
                await view_controller.check_campaigns_claim_status(cookies_file, progress_file)
                await asyncio.sleep(60)
            else:
                # Стрим завершился нормально (по таймеру)
                print(tl.c["finish_view"].format(username=username))
                print(f"\n{tl.c['waitcd300seconds']}")
                # check drops
                await view_controller.check_campaigns_claim_status(cookies_file, progress_file)
                await asyncio.sleep(300)

        except Exception as e:
            print(tl.c["error_viewing"].format(e=e))
            print(f"\n{tl.c['waitcd120seconds']}")
            await asyncio.sleep(120)


async def start_streamer_drops(cookies_file, progress_file):
    while True:
        streamers_data = formatter.collect_usernames(json_filename=progress_file)
        found_online = False
        stream_ended = False
        print(f"\n{tl.c['search_streamers']}")

        for streamer in streamers_data:
            username = streamer["username"]
            required_seconds = streamer["required_seconds"]
            claim_status = streamer["claim"]

            # Проверяем, нужно ли получать дроп
            if claim_status == 1:
                print(tl.c["streamer_time_skip"].format(username=username))
                continue

            # Проверяем, осталось ли время для просмотра
            remaining = await formatter.get_remaining_time(username, json_filename=progress_file)
            if remaining <= 0:
                print(tl.c["streamer_time_skip"].format(username=username))
                continue

            stream_info = await kick.get_stream_info(username)

            if stream_info["is_live"] and stream_info["game_id"] == CATEGORY_ID:
                print(tl.c["streamer_found"].format(username=username))
                print(tl.c["starting_view_streamer"].format(remaining=remaining))
                # Запускаем фарм для этого стримера
                found_online = True
                stream_ended = await view_controller.run_with_timer(
                    partial(view_controller.view_stream, username, CATEGORY_ID, cookies_file, progress_file),
                    required_seconds + 120
                )

                # Если стример закончил или сменил игру
                if stream_ended:
                    print(tl.c["streamer_play_another_game"].format(username=username))
                    print(f"\n{tl.c['waitcd120seconds']}")
                    await asyncio.sleep(120)
                    break  # Выходим из цикла for, чтобы начать новый поиск
                else:
                    # Стрим завершился нормально (по таймеру)
                    print(tl.c["finish_view"].format(username=username))
                    # Проверяем оставшееся время
                    remaining_after = await formatter.get_remaining_time(username, json_filename=progress_file)
                    print(remaining_after)
                    if remaining_after > 0:
                        print(f"\n{tl.c['waitcd120seconds']}")
                        await asyncio.sleep(120)
                        break  # Ищем следующего онлайн стримера
                    else:
                        print(tl.c["finish_view"].format(username=username))
                        await asyncio.sleep(60)
                        break
            else:
                print(tl.c["streamer_offline"].format(username=username))

        # Если никто не онлайн
        if not found_online:
            print(f"\n{tl.c['all_streamers_offline']}")
            print(f"\n{tl.c['wait_streamers_online']}")
            # check drops
            await view_controller.check_campaigns_claim_status(cookies_file, progress_file)
            rndstreamercategory = kick.get_random_stream_from_category(CATEGORY_ID)
            if rndstreamercategory and rndstreamercategory.get("username"):
                stream_ended = await view_controller.run_with_timer(
                    partial(view_controller.view_stream, rndstreamercategory["username"], CATEGORY_ID, cookies_file, progress_file),
                    3600
                )
            await asyncio.sleep(600)


async def run_account(acc, mode):
    """Точка входа одного аккаунта (выполняется в своём потоке / event loop)."""
    # Пока ник не определён — метим логи именем файла.
    logger.set_label(acc["fallback_label"])

    cookies = cookies_manager.load_cookies(acc["cookies_file"])
    if not cookies:
        print(tl.c["account_cookies_invalid"].format(file=acc["cookies_file"]))
        return

    # Резолвим ник с Kick, при неудаче — остаёмся на имени файла.
    nick = kick.get_account_username(cookies)
    if nick:
        logger.set_label(nick)
        print(tl.c["account_nick_resolved"].format(nick=nick))
    else:
        print(tl.c["account_nick_fallback"].format(fallback=acc["fallback_label"]))

    # Синхронизируем/клеймим дропы перед стартом цикла.
    await view_controller.check_campaigns_claim_status(acc["cookies_file"], acc["progress_file"])

    if mode == "1":
        await start_streamer_drops(acc["cookies_file"], acc["progress_file"])
    elif mode == "2":
        await start_general_drops(acc["cookies_file"], acc["progress_file"])


def _thread_entry(acc, mode):
    """Обёртка потока: свой event loop на аккаунт (в kick.py есть блокирующие
    вызовы, поэтому нельзя держать все аккаунты в одном общем loop)."""
    try:
        asyncio.run(run_account(acc, mode))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(tl.c["critical_error"].format(e=e))
        traceback.print_exc()


def main():
    print(tl.c["links"])
    print("Thanks Mixanicys")

    accounts = discover_accounts()
    if not accounts:
        print(tl.c["no_accounts_found"].format(max=MAX_ACCOUNTS))
        return

    slots = ", ".join(str(a["slot"]) for a in accounts)
    print(tl.c["accounts_found"].format(count=len(accounts), slots=slots))

    mode = choose_mode()
    if mode == "0":
        print(f"\n{tl.c['exit_script']}")
        return

    print(f"\n{tl.c['launching']}...")

    # Один запрос кампаний на всех + создание недостающих файлов прогресса.
    template = build_template()
    ensure_progress_files(accounts, template)

    threads = []
    for acc in accounts:
        t = threading.Thread(
            target=_thread_entry,
            args=(acc, mode),
            name=acc["fallback_label"],
            daemon=True,
        )
        t.start()
        threads.append(t)
        print(tl.c["account_starting"].format(slot=acc["slot"], file=acc["cookies_file"]))

    print(f"\n{tl.c['all_accounts_started'].format(count=len(threads))}")

    # Ждём потоки. Они daemon и крутят бесконечный цикл фарма — завершатся
    # только по Ctrl+C (тогда процесс закрывается вместе с потоками).
    try:
        while any(t.is_alive() for t in threads):
            for t in threads:
                t.join(timeout=0.5)
    except KeyboardInterrupt:
        print(f"\n\n{tl.c['exit_script']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{tl.c['exit_script']}")
    except Exception as e:
        print(f"\n{tl.c['critical_error'].format(e=e)}")
        traceback.print_exc()
