# Website Blocker

A clean, cross-platform **Website Blocker** implemented in Python.  
It edits the system **hosts** file to redirect specified domains to `127.0.0.1`, effectively blocking them.

- ✅ Tkinter GUI (simple & fast)
- ✅ CLI for automation (`--block`, `--unblock`, `--list`)
- ✅ Cross-platform hosts detection (Windows / Linux / macOS)
- ✅ Safe & idempotent rules with a marker: `# website-blocker`
- ✅ Unit tests (no admin needed; tests use a temp hosts file)
- ✅ GitHub-ready structure (src/, tests/, CI, Ruff/Black, MIT)

> ⚠️ Modifying the real hosts file requires **administrator/root** privileges.

## Install & Run

```bash
# clone
git clone https://github.com/mobinyousefi-cs/website-blocker.git
cd website-blocker

# (optional) create venv
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate

# dev tools
pip install -r requirements.txt

# run GUI
python -m website_blocker
