#!/usr/bin/env bash
# Installer for cdhai-social-media-officer-linkedin.skill v0.4.0
#
# Creates ~/.cdhai-linkedin-skill/ with memory + config templates.
# Installs Python dependencies. Symlinks the skill into ~/.codex/skills/.
# Existing memory and config are preserved on re-install.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="cdhai-social-media-officer-linkedin"
HOME_BASE="$HOME/.cdhai-linkedin-skill"
CACHE_DIR="$HOME_BASE/cache"
MEMORY_DIR="$HOME_BASE/memory"
CODEX_SKILLS_DIR="$HOME/.codex/skills"
VERSION_FILE="$SKILL_DIR/VERSION"
VERSION="$(cat "$VERSION_FILE" 2>/dev/null || echo unknown)"

echo "=================================================="
echo "  CDHAI LinkedIn Skill — installer (v$VERSION)"
echo "=================================================="

# ----- Python dependencies -----
echo ""
echo "[1/5] Installing Python dependencies (deterministic helpers only)..."
python3 -m pip install --break-system-packages --quiet \
    pypdf \
    python-docx \
    Pillow \
    requests \
    beautifulsoup4 \
    || {
        echo "  Falling back without --break-system-packages..."
        python3 -m pip install --quiet \
            pypdf python-docx Pillow requests beautifulsoup4
    }
echo "  ✓ Done. (No openai package needed — Codex handles all AI work natively.)"

# ----- ~/.cdhai-linkedin-skill/ layout -----
echo ""
echo "[2/5] Setting up home directory at $HOME_BASE..."
mkdir -p "$HOME_BASE" "$CACHE_DIR" "$MEMORY_DIR"
echo "  ✓ Directories ready."

# ----- Memory templates (only if missing — never overwrite user memory) -----
echo ""
echo "[3/5] Initializing memory templates (preserving existing)..."
for f in user_memory.md memory_change_log.md; do
    dest="$MEMORY_DIR/$f"
    if [ -f "$dest" ]; then
        echo "  - $f exists, preserved."
    else
        cp "$SKILL_DIR/_memory_template/$f" "$dest"
        echo "  - $f initialized."
    fi
done

# ----- config.json (only if missing) -----
CONFIG_FILE="$HOME_BASE/config.json"
if [ -f "$CONFIG_FILE" ]; then
    echo ""
    echo "[4/5] config.json exists — preserved."
    echo "  Edit it manually to add or update API keys."
else
    echo ""
    echo "[4/5] Writing fresh config.json template..."
    cat > "$CONFIG_FILE" <<'EOF'
{
  "serpapi_key": "",
  "github_version_check": true,
  "language": "en"
}
EOF
    echo "  ✓ Created $CONFIG_FILE."
    echo "    No API keys are required for v0.4.2 — Codex handles all AI work natively."
    echo "    Optional: add serpapi_key for cleaner Tier 2 face-identification web search"
    echo "    (falls back to DuckDuckGo if absent)."
fi

# ----- Symlink into Codex skills directory -----
echo ""
echo "[5/5] Symlinking skill into Codex skills directory..."
mkdir -p "$CODEX_SKILLS_DIR"
LINK_PATH="$CODEX_SKILLS_DIR/$SKILL_NAME.skill"
if [ -L "$LINK_PATH" ] || [ -e "$LINK_PATH" ]; then
    rm -f "$LINK_PATH"
fi
ln -s "$SKILL_DIR" "$LINK_PATH"
echo "  ✓ Symlinked: $LINK_PATH → $SKILL_DIR"

echo ""
echo "=================================================="
echo "  Install complete."
echo ""
echo "  No API keys are required for default use. Codex"
echo "  (your runtime) handles all AI/vision/LLM tasks natively."
echo ""
echo "  To use:"
echo "    1. Copy _template/content_template.docx into your working folder."
echo "    2. Fill it in (Purpose, Post Type, Date, Key Points)."
echo "    3. Drop any supporting PDFs / images into the same folder."
echo "    4. In Codex App: \"Use the cdhai-social-media-officer-linkedin skill on this folder\""
echo "=================================================="
