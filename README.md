# MultiKickAutoDrops

[RU](https://github.com/NoDwor/multikickautodrops/blob/main/README.ru.md) · [EN](https://github.com/NoDwor/multikickautodrops/blob/main/README.md)

---

**MultiKickAutoDrops** is a minimalist automation tool that farms **Rust** game drops from [Kick.com](https://kick.com) without actually watching any stream — and it farms **several accounts in parallel**. It runs in the background, simulating stream viewing through Kick.com's API, so you collect drops while saving bandwidth and system resources.

## ✨ Features

- 🎮 Auto-farms **Rust** drops on Kick.com — no video or audio is ever downloaded
- 👥 **Multi-account** — drop in several cookie files and each one farms **in parallel**, in its own thread
- 💾 Minimal resources — API requests only, no media stream
- 📈 Per-account progress is saved between restarts (`views/<name>.json`)
- 🌐 Bilingual interface (RU / EN)

## ⚙️ How It Works

Every **10 seconds** the app simulates watching a stream by fetching stream metadata and sending the requests Kick.com expects — this is enough to advance drop timers, **without downloading any video or audio data**.

To keep channel status accurate (ONLINE / OFFLINE), it also opens a **WebSocket** connection that receives real-time events:
- Streams going online / offline
- Game / category changes
- Drop progress updates
- Viewer count changes

## 🧩 Installation

### Option 1: Pre-built release (Windows)

1. Open the [Releases](https://github.com/NoDwor/multikickautodrops/releases) page
2. Download the latest build — `KickAutoDrops-windows.zip`
3. Extract the archive. Keep the `locales/` folder and `example_config.ini` **next to the executable**.
4. Install a cookie-export extension:
   - [Get cookies.txt LOCALLY (Chrome)](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - [Get cookies.txt LOCALLY (Firefox)](https://addons.mozilla.org/en-US/firefox/addon/get-cookies-txt-locally/)
5. Log in to [kick.com](https://kick.com) and export all cookies
6. Save them into a `.txt` file (e.g. **`cookies.txt`**) next to the executable — you can add several files for several accounts (see the "👥 Accounts & cookies" section below)
7. Run the executable from a terminal / command prompt

### Option 2: Build from source

```bash
# Clone the repository
git clone https://github.com/NoDwor/multikickautodrops.git
cd multikickautodrops

# Install dependencies
pip install -r requirements.txt

# Run from source
python index.py

# — or build a standalone executable —
pip install pyinstaller
pyinstaller index.spec
```

## 👥 Accounts & cookies

The app auto-discovers every account from the cookie files in the project root — you don't need to configure how many there are.

- Export your cookies from [kick.com](https://kick.com) with the **Get cookies.txt LOCALLY** extension — it saves a file in the **Netscape** format (first line `# Netscape HTTP Cookie File`).
- Drop the file next to the executable (or in the project root when running from source). **Every `*.txt` in Netscape format counts as a separate account**; the name is arbitrary: `cookies1.txt`, `main.txt`, `nick.txt`.
- Need **multiple accounts**? Just add several such files — they all farm **in parallel**.
- `requirements.txt` and other non-cookie `.txt` files are skipped automatically.
- Each account's progress is stored separately in `views/<filename>.json`, and logs are tagged with the account's file name.

> ⚠️ A cookie file contains your `session_token` — effectively account access. These files are already in `.gitignore`; **never commit or publish them.**

## ❤️ Contributing

Want to add a feature, improve the code, or help with translations? **Fork [the repository](https://github.com/NoDwor/multikickautodrops)** and open a **pull request** — all contributions are welcome and appreciated!

## 📄 License

Released under the [MIT License](LICENSE).

<sub>Based on [kickautodrops](https://github.com/PBA4EVSKY/kickautodrops) by PBA4EVSKY, with parallel multi-account farming added.</sub>
