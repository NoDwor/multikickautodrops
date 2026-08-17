# MultiKickAutoDrops

[RU](https://github.com/NoDwor/multikickautodrops/blob/main/README.ru.md) · [EN](https://github.com/NoDwor/multikickautodrops/blob/main/README.md)

---

**MultiKickAutoDrops** is a minimalist automation tool that farms **Rust** game drops from [Kick.com](https://kick.com) without actually watching any stream — and it farms **several accounts in parallel**. It runs in the background, simulating stream viewing through Kick.com's API, so you collect drops while saving bandwidth and system resources.

## ✨ Features

- 🎮 Auto-farms **Rust** drops on Kick.com — no video or audio is ever downloaded
- 👥 **Multi-account** — drop in several cookie files and each one farms **in parallel**, in its own thread
- 💾 Minimal resources — API requests only, no media stream
- 📈 Per-account progress is saved between restarts (`views/<name>.json`)
- 🏆 Optional **auto-claim** of completed drops
- 🌐 Bilingual interface (RU / EN)

## ⚙️ How It Works

The app opens a **WebSocket** connection to Kick's viewer endpoint and keeps the "watch" session alive:

- every **~15 seconds** it sends keep-alive `ping` / handshake frames;
- every **60 seconds** it sends the `watch.livestream` event that Kick counts as watch time — **without downloading any video or audio**;
- it periodically re-checks the stream and stops if the streamer goes **offline** or switches to a **different game**.

Completed rewards are detected from Kick's drops API and, if enabled, **claimed automatically**.

## 🧩 Installation

### Option 1: Pre-built release (Windows)

1. Open the [Releases](https://github.com/NoDwor/multikickautodrops/releases) page
2. Download the latest build — `KickAutoDrops-windows.zip`
3. Extract the archive. Keep the `locales/` folder and `example_config.ini` **next to `KickAutoDrops.exe`**.
4. Install a cookie-export extension:
   - [Get cookies.txt LOCALLY (Chrome)](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - [Get cookies.txt LOCALLY (Firefox)](https://addons.mozilla.org/en-US/firefox/addon/get-cookies-txt-locally/)
5. Log in to [kick.com](https://kick.com) and export all cookies
6. Save them into a `.txt` file (e.g. **`cookies.txt`**) **next to the executable** — you can add several files for several accounts (see the "👥 Accounts & cookies" section below)
7. Run `KickAutoDrops.exe` (double-click it, or launch it from a terminal)

### Option 2: Build from source

Requires **Python 3.11+**.

```bash
# 1. Clone the repository
git clone https://github.com/NoDwor/multikickautodrops.git
cd multikickautodrops

# 2. Install dependencies
pip install -r requirements.txt
```

3. **Export your Kick cookies into a `.txt` file and put it in this folder** (see "👥 Accounts & cookies"). Without at least one cookie file the app prints "no accounts found" and exits.

```bash
# 4. Run it
python index.py
```

On Windows you can also just double-click **`run.bat`** — it picks up `py`/`python` automatically and keeps the console window open so you can read the output.

`config.ini` is created automatically from `example_config.ini` on first run — no manual setup needed.

To build a standalone executable instead:

```bash
pip install pyinstaller
pyinstaller index.spec   # result appears in dist/
```

## 👥 Accounts & cookies

The app auto-discovers every account from the cookie files in the project root — you don't need to configure how many there are.

- Export your cookies from [kick.com](https://kick.com) with the **Get cookies.txt LOCALLY** extension — it saves a file in the **Netscape** format (first line `# Netscape HTTP Cookie File`).
- Drop the file next to the executable (or in the project root when running from source). **Every `*.txt` in Netscape format counts as a separate account**; the name is arbitrary: `cookies1.txt`, `main.txt`, `nick.txt`.
- Need **multiple accounts**? Just add several such files — they all farm **in parallel**.
- `requirements.txt` and other non-cookie `.txt` files are skipped automatically.
- Each account's progress is stored separately in `views/<filename>.json`, and logs are tagged with the account's file name.

> ⚠️ A cookie file contains your `session_token` — effectively account access. These files are already in `.gitignore`; **never commit or publish them.**

## 🛠 Configuration

Settings live in `config.ini` (auto-created from `example_config.ini`):

```ini
[general]
language = en          ; interface language: en / ru
autoclaimdrops = true  ; automatically claim completed drops
```

## 🙏 Credits

This project is built on the original [**kickautodrops**](https://github.com/PBA4EVSKY/kickautodrops) by **[PBA4EVSKY](https://github.com/PBA4EVSKY)** — the starter code comes from that project. MultiKickAutoDrops adds parallel multi-account farming on top.

## 📄 License

Released under the [MIT License](LICENSE).
