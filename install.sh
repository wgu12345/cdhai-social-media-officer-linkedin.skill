#!/usr/bin/env bash
# install.sh — v0.4.3
#
# Idempotent installer for the writer skill. Safe to re-run on existing
# installs; only adds what is missing, does not overwrite user data.
#
# Replace the existing install.sh in your skill repo with this file.

set -e

SKILL_HOME="${HOME}/.cdhai-linkedin-skill"
MEMORY_DIR="${SKILL_HOME}/memory"
CACHE_DIR="${SKILL_HOME}/cache"
CONFIG="${SKILL_HOME}/config.json"

# Resolve the directory this script lives in (the skill repo root).
REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "==> Installing cdhai-social-media-officer-linkedin (v0.4.3)"
echo "    Repo: ${REPO_DIR}"
echo "    Home: ${SKILL_HOME}"

# --------------------------------------------------------------------------
# 1. Create skill home + subdirs
# --------------------------------------------------------------------------
mkdir -p "${MEMORY_DIR}" "${CACHE_DIR}"

# --------------------------------------------------------------------------
# 2. Seed user_memory.md if it doesn't already exist
#    v0.4.3 ships team-baseline rules as a starter so new installs don't
#    start from empty memory (which was the root cause of the team-member
#    quality regression we hit in v0.4.2 testing).
# --------------------------------------------------------------------------
USER_MEMORY="${MEMORY_DIR}/user_memory.md"
STARTER="${REPO_DIR}/_memory_template/user_memory.md"

if [ ! -f "${USER_MEMORY}" ]; then
  if [ -f "${STARTER}" ]; then
    cp "${STARTER}" "${USER_MEMORY}"
    echo "    ✓ Seeded user_memory.md with v0.4.3 CDHAI team baseline."
  else
    touch "${USER_MEMORY}"
    echo "    ! Starter template not found; created empty user_memory.md."
  fi
else
  echo "    ✓ user_memory.md already present, leaving untouched."
fi

# --------------------------------------------------------------------------
# 3. Seed config.json if missing
# --------------------------------------------------------------------------
if [ ! -f "${CONFIG}" ]; then
  cat > "${CONFIG}" <<'JSON'
{
  "skill_version": "0.4.3",
  "image_diversity_cap_per_subject": 2,
  "image_diversity_cap_per_scene": 2,
  "min_images_per_post": 5,
  "reviewer_revision_loop_max": 3,
  "hard_contracts_enforced": true
}
JSON
  echo "    ✓ Created config.json."
else
  echo "    ✓ config.json already present, leaving untouched."
fi

# --------------------------------------------------------------------------
# 4. Make helpers executable
# --------------------------------------------------------------------------
chmod +x "${REPO_DIR}/_helpers/"*.py 2>/dev/null || true
echo "    ✓ Helper scripts marked executable."

# --------------------------------------------------------------------------
# 5. Smoke-test python-docx availability (validate_template.py needs it)
# --------------------------------------------------------------------------
if ! python3 -c "import docx" 2>/dev/null; then
  echo ""
  echo "    !! python-docx is not installed. Install it now with:"
  echo "       pip3 install python-docx"
  echo ""
fi

echo ""
echo "==> v0.4.3 install complete."
echo "    Memory file: ${USER_MEMORY}"
echo "    Run the skill in Codex by pointing it at a folder that contains"
echo "    a filled content.docx (template fields: Purpose, Post Type,"
echo "    Date, Key Points, Background, Notes)."
