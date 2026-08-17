# KickAutoDrops

[RU](https://github.com/PBA4EVSKY/kickautodrops/blob/main/README.ru.md) [EN](https://github.com/PBA4EVSKY/kickautodrops/blob/main/README.md)

---

KickAutoDrops is a minimalist automation tool designed to efficiently collect Rust game drops from Kick.com without actually streaming any video or audio content. The application runs in the background, simulating stream viewing by interacting with Kick.com's API, allowing you to collect drops while saving bandwidth and system resources.

## ⚙️ How It Works
Every 10 seconds, the application simulates watching a stream by fetching stream metadata and sending the necessary requests to Kick.com - this is sufficient to progress drop timers. Crucially, this completely bypasses downloading any actual video or audio stream data. To maintain accurate channel status (ONLINE/OFFLINE), the application establishes a websocket connection that receives real-time events about:
- Streams going online or offline
- Game/category changes
- Drop progress updates
- Viewer count changes


## 🧩 Installation
### 1: Pre-built Release

1. Navigate to the [Releases](https://github.com/PBA4EVSKY/kickautodrops/releases) section
2. Download the latest version for your platform (Windows/Linux/macOS)
3. Extract the executable
4. Install extension [Get cookies.txt LOCALLY for chrome](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) or [Get cookies.txt LOCALLY for firefox](https://addons.mozilla.org/en-US/firefox/addon/get-cookies-txt-locally/) 
5. Export all cookies from kick.com
6. Save them into a `.txt` file (e.g. **`cookies.txt`**) next to the executable — you can add several files for several accounts (see the "👥 Accounts & cookies" section below)
7. Run from terminal/command prompt

### 3: Build from Source

```
# Clone the repository
git clone https://github.com/PBA4EVSKY/kickautodrops.git

# Navigate to the directory
cd kickautodrops

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
- Drop the file into the project root. **Every `*.txt` in Netscape format counts as a separate account**; the name is arbitrary: `cookies1.txt`, `main.txt`, `nick.txt`.
- Need **multiple accounts**? Just add several such files — they all farm **in parallel**.
- `requirements.txt` and other non-cookie `.txt` files are skipped automatically.
- Each account's progress is stored separately in `views/<filename>.json`, and logs are tagged with the account's file name.

> ⚠️ A cookie file contains your `session_token` — effectively account access. These files are already in `.gitignore`; **never commit or publish them.**

## ❤️Contributing

If you’d like to add a new feature, improve existing code, or help with translations, feel free to **fork this repository** and submit a **pull request**.  
All contributions are welcome and appreciated!
