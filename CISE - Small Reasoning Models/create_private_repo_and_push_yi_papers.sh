#!/usr/bin/env bash
set -euo pipefail

# Create a private GitHub repository and push Yi Ding publication PDFs.
# Defaults assume Google Drive Desktop sync path on macOS.
# Requirements: python3, git, and either GitHub CLI (`gh auth login`) or GITHUB_TOKEN.
# Optional: git-lfs for cleaner PDF storage.

REPO_NAME="${REPO_NAME:-yi-papers}"
GITHUB_OWNER="${GITHUB_OWNER:-yding37}"
CSV_PATH="${CSV_PATH:-./yi_publications.csv}"
PROJECT_DIR="${PROJECT_DIR:-/Users/yding37/Google Drive/My Drive/proposals/CISE - Small Reasoning Models}"
PAPERS_DIR="${PAPERS_DIR:-$PROJECT_DIR/yi-papers}"
UNPAYWALL_EMAIL="${UNPAYWALL_EMAIL:-}"
VISIBILITY="private"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOWNLOADER="$SCRIPT_DIR/download_yi_publication_pdfs.py"

if [[ ! -f "$CSV_PATH" ]]; then
  echo "CSV not found: $CSV_PATH" >&2
  echo "Set CSV_PATH=/path/to/yi_publications.csv or run from the folder containing it." >&2
  exit 1
fi
if [[ ! -f "$DOWNLOADER" ]]; then
  echo "Downloader not found: $DOWNLOADER" >&2
  exit 1
fi

mkdir -p "$PAPERS_DIR"

python3 -m pip show requests beautifulsoup4 >/dev/null 2>&1 || \
  python3 -m pip install --user requests beautifulsoup4

DOWNLOAD_ARGS=(--csv "$CSV_PATH" --out "$PAPERS_DIR")
if [[ -n "$UNPAYWALL_EMAIL" ]]; then
  DOWNLOAD_ARGS+=(--email "$UNPAYWALL_EMAIL")
fi
python3 "$DOWNLOADER" "${DOWNLOAD_ARGS[@]}"

cd "$PAPERS_DIR"

cat > README.md <<EOF
# Yi Ding publication PDFs

Private archive of publication PDFs for NSF proposal work.

Source publication list: Google Scholar CSV export.

Generated files:
- \`download_manifest.csv\`: download status, source URL, and metadata for each listed paper.
- \`*.pdf\`: downloaded publication PDFs where an open PDF source was found.

EOF

cp "$CSV_PATH" ./yi_publications.csv

if [[ ! -d .git ]]; then
  git init
fi

if command -v git-lfs >/dev/null 2>&1; then
  git lfs install --local
  git lfs track "*.pdf"
  git add .gitattributes
fi

git add README.md yi_publications.csv download_manifest.csv *.pdf 2>/dev/null || true
if git diff --cached --quiet; then
  echo "No new files to commit."
else
  git commit -m "Add Yi Ding publication PDFs"
fi

FULL_REPO="$GITHUB_OWNER/$REPO_NAME"

if command -v gh >/dev/null 2>&1; then
  if ! gh repo view "$FULL_REPO" >/dev/null 2>&1; then
    gh repo create "$FULL_REPO" --private --source=. --remote=origin --push
  else
    git remote remove origin 2>/dev/null || true
    git remote add origin "git@github.com:$FULL_REPO.git"
    git branch -M main
    git push -u origin main
  fi
else
  if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    echo "Install GitHub CLI and run 'gh auth login', or set GITHUB_TOKEN with repo scope." >&2
    exit 1
  fi
  api_status=$(curl -sS -o /tmp/create_repo_response.json -w "%{http_code}" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"$REPO_NAME\",\"private\":true}")
  if [[ "$api_status" != "201" && "$api_status" != "422" ]]; then
    cat /tmp/create_repo_response.json >&2
    exit 1
  fi
  git remote remove origin 2>/dev/null || true
  git remote add origin "https://github.com/$FULL_REPO.git"
  git branch -M main
  git push -u origin main
fi

echo "Done: https://github.com/$FULL_REPO"
