import builtins
import sys
import threading

# Потоко-локальный префикс: у каждого аккаунта (потока) свой ник.
_local = threading.local()
# Один общий замок, чтобы многострочные print из разных потоков не смешивались.
_lock = threading.Lock()
# Сохраняем оригинальный print ДО подмены.
_orig_print = builtins.print
_installed = False


def set_label(label: str):
    """Задать префикс (ник аккаунта) для текущего потока."""
    _local.prefix = f"[{label}] " if label else ""


def get_label() -> str:
    return getattr(_local, "prefix", "")


def _wrapped_print(*args, sep=" ", end="\n", file=None, flush=False):
    if file is None:
        file = sys.stdout

    prefix = getattr(_local, "prefix", "")
    text = sep.join(str(a) for a in args)

    if prefix:
        # Префикс дописываем к каждой непустой строке, чтобы ведущие '\n'
        # (используются в коде как разделители) оставались настоящими отступами.
        lines = text.split("\n")
        text = "\n".join((prefix + line) if line else line for line in lines)

    with _lock:
        _orig_print(text, end=end, file=file, flush=flush)


def install():
    """Один раз подменить builtins.print. Все существующие print во всех
    модулях начнут автоматически получать префикс текущего потока."""
    global _installed
    if not _installed:
        # Windows-консоль/пайп часто работает в cp1252 — принудительно переводим
        # вывод в UTF-8 с errors="replace", иначе эмодзи/галочки в строках локали
        # (✓, ❌, 🔍 …) роняют print с UnicodeEncodeError.
        for _stream in (sys.stdout, sys.stderr):
            try:
                _stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, ValueError, OSError):
                pass
        builtins.print = _wrapped_print
        _installed = True
