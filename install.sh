#!/usr/bin/env bash
# install.sh — Bootstrap for cdhai-social-media-officer-linkedin.skill v0.3.0
#
# Usage:
#   bash install.sh
#
# What it does:
#   1. Creates ~/.cdhai-linkedin-skill/ (config + memory + cache)
#   2. Installs Python dependencies
#   3. Copies memory templates on first install (preserves existing memory on re-install)
#   4. Creates default config.json if missing
#   5. Tries to symlink into ~/.codex/skills/ if Codex CLI is installed

set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
HOME_DIR="$HOME/.cdhai-linkedin-skill"

echo "==> Installing cdhai-social-media-officer-linkedin v$(cat "$SKILL_DIR/VERSION")"
echo "    Source: $SKILL_DIR"
echo "    Target: $HOME_DIR"
echo ""

# 1. Create home directory structure
mkdir -p "$HOME_DIR/memory" "$HOME_DIR/cache"

# 2. Python dependencies
echo "==> Installing Python dependencies"
PIP_CMD="pip3"
if ! command -v pip3 >/dev/null 2>&1; then
  PIP_CMD="pip"
fi

# --break-system-packages is needed on macOS Python 3.11+ system Python.
# Falls back gracefully if not supported.
$PIP_CMD install --quiet python-docx Pillow pypdf requests beautifulsoup4 \
  --break-system-packages 2>/dev/null || \
  $PIP_CMD install --quiet python-docx Pillow pypdf requests beautifulsoup4

echo "  ✓ python-docx, Pillow, pypdf, requests, beautifulsoup4 installed"

# 3. Copy memory templates on first install
if [ ! -f "$HOME_DIR/memory/user_memory.md" ]; then
  cp "$SKILL_DIR/_memory_template/user_memory.md" "$HOME_DIR/memory/"
  echo "  ✓ user_memory.md initialized"
else
  echo "  · user_memory.md already exists — preserved"
fi

if [ ! -f "$HOME_DIR/memory/memory_change_log.md" ]; then
  cp "$SKILL_DIR/_memory_template/memory_change_log.md" "$HOME_DIR/memory/"
  echo "  ✓ memory_change_log.md initialized"
else
  echo "  · memory_change_log.md already exists — preserved"
fi

# 4. Default config.json
if [ ! -f "$HOME_DIR/config.json" ]; then
  cat > "$HOME_DIR/config.json" <<EOF
{
  "unsplash_access_key": "",
  "openai_api_key": "",
  "github_version_check": true,
  "language": "en"
}
EOF
  echo "  ✓ config.json initialized (fill in API keys to enable Unsplash / DALL-E)"
else
  echo "  · config.json already exists — preserved"
fi

# 5. Symlink into Codex CLI skills dir if it exists
CODEX_SKILLS_DIR="$HOME/.codex/skills"
if [ -d "$CODEX_SKILLS_DIR" ]; then
  LINK_TARGET="$CODEX_SKILLS_DIR/cdhai-social-media-officer-linkedin.skill"
  if [ ! -L "$LINK_TARGET" ] && [ ! -e "$LINK_TARGET" ]; then
    ln -s "$SKILL_DIR" "$LINK_TARGET"
    echo "  ✓ symlinked into $CODEX_SKILLS_DIR"
  else
    echo "  · symlink already exists in $CODEX_SKILLS_DIR"
  fi
else
  echo "  · Codex CLI not detected (~/.codex/skills/ not found)"
  echo "    If you're using Codex App, install via Plugins → 'Install from URL'"
fi

echo ""
echo "==> Install complete."
echo ""
echo "Next steps:"
echo "  1. Fill in API keys (optional): nano $HOME_DIR/config.json"
echo "  2. Verify: cat $HOME_DIR/config.json"
echo "  3. In Codex: 'Use the cdhai-social-media-officer-linkedin skill on this folder'"
