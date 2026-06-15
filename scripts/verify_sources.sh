#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/manifests/sources.tsv"
FOCUS="$ROOT/manifests/focus_paths.tsv"
CHECK_REMOTE=0
REMOTE_ONLY=0
ALLOW_MISSING=0
TIER="required"

usage() {
  cat <<'EOF'
Usage: scripts/verify_sources.sh [--tier required|important|adjacent|all] [--remote] [--remote-only] [--allow-missing]

Verify manifests, local checkouts, and focus paths. Without --remote, this does
not call the network. Missing local checkouts fail for the selected tier unless
--allow-missing is passed. --remote-only validates manifest URLs without
requiring local checkouts.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tier)
      TIER="${2:?missing tier}"
      shift 2
      ;;
    --remote)
      CHECK_REMOTE=1
      shift
      ;;
    --remote-only)
      CHECK_REMOTE=1
      REMOTE_ONLY=1
      shift
      ;;
    --allow-missing)
      ALLOW_MISSING=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

include_tier() {
  local row_tier="$1"
  case "$TIER" in
    required) [[ "$row_tier" == "required" ]] ;;
    important) [[ "$row_tier" == "required" || "$row_tier" == "important" ]] ;;
    adjacent|all) [[ "$row_tier" == "required" || "$row_tier" == "important" || "$row_tier" == "adjacent" ]] ;;
    *) echo "invalid tier: $TIER" >&2; exit 2 ;;
  esac
}

git_ls_remote_head() {
  local url="$1"
  GIT_TERMINAL_PROMPT=0 git \
    -c protocol.version=2 \
    -c http.lowSpeedLimit=1 \
    -c http.lowSpeedTime=20 \
    ls-remote "$url" HEAD >/dev/null 2>&1
}

tmp_ids="$(mktemp)"
tmp_paths="$(mktemp)"
trap 'rm -f "$tmp_ids" "$tmp_paths"' EXIT

errors=0

echo "Checking source manifest structure..."
while IFS=$'\t' read -r tier category id path url recurse default_count notes; do
  [[ -n "${tier:-}${category:-}${id:-}${path:-}${url:-}" ]] || continue
  if [[ -z "${tier:-}" || -z "${category:-}" || -z "${id:-}" || -z "${path:-}" || -z "${url:-}" ]]; then
    echo "BAD_ROW $tier $category $id $path $url" >&2
    errors=$((errors + 1))
    continue
  fi
  if [[ "$id" == *"/"* ]]; then
    echo "BAD_ID_CONTAINS_SLASH $id" >&2
    errors=$((errors + 1))
    continue
  fi
  printf "%s\n" "$id" >> "$tmp_ids"
  printf "%s\n" "$path" >> "$tmp_paths"
done < <(tail -n +2 "$MANIFEST")

dupes="$(sort "$tmp_ids" | uniq -d)"
if [[ -n "$dupes" ]]; then
  echo "DUPLICATE_IDS:" >&2
  echo "$dupes" >&2
  errors=$((errors + 1))
fi

path_dupes="$(sort "$tmp_paths" | uniq -d)"
if [[ -n "$path_dupes" ]]; then
  echo "DUPLICATE_PATHS:" >&2
  echo "$path_dupes" >&2
  errors=$((errors + 1))
fi

echo "Checking focus manifest references..."
while IFS=$'\t' read -r id focus_path why; do
  [[ -n "${id:-}${focus_path:-}${why:-}" ]] || continue
  if [[ "$id" == *"/"* ]]; then
    echo "BAD_FOCUS_ID_CONTAINS_SLASH $id" >&2
    errors=$((errors + 1))
    continue
  fi
  if ! grep -qxF "$id" "$tmp_ids"; then
    echo "UNKNOWN_FOCUS_ID $id $focus_path" >&2
    errors=$((errors + 1))
    continue
  fi
done < <(tail -n +2 "$FOCUS")

echo "Checking local checkouts and focus paths for tier=$TIER..."
while IFS=$'\t' read -r tier category id path url recurse default_count notes; do
  [[ -n "${tier:-}${category:-}${id:-}${path:-}${url:-}" ]] || continue
  include_tier "$tier" || continue
  abs="$ROOT/$path"

  if [[ "$REMOTE_ONLY" == "1" ]]; then
    if git_ls_remote_head "$url"; then
      echo "REMOTE_OK $tier $id $url"
    else
      echo "REMOTE_UNREACHABLE $tier $id $url" >&2
      errors=$((errors + 1))
    fi
    continue
  fi

  if [[ ! -d "$abs/.git" ]]; then
    echo "MISSING_CHECKOUT $tier $id $path"
    if [[ "$ALLOW_MISSING" != "1" ]]; then
      errors=$((errors + 1))
    fi
    continue
  fi

  if ! git -C "$abs" rev-parse --verify HEAD >/dev/null 2>&1; then
    echo "BAD_HEAD $id $path" >&2
    errors=$((errors + 1))
    continue
  fi

  if [[ "$CHECK_REMOTE" == "1" ]]; then
    if ! git_ls_remote_head "$url"; then
      echo "REMOTE_UNREACHABLE $id $url" >&2
      errors=$((errors + 1))
    fi
  fi

  while IFS= read -r focus_path; do
    [[ -n "$focus_path" ]] || continue
    if [[ "$focus_path" == *"*"* ]]; then
      if ! compgen -G "$abs/$focus_path" >/dev/null; then
        echo "MISSING_FOCUS $id $focus_path"
        errors=$((errors + 1))
      fi
    elif [[ ! -e "$abs/$focus_path" ]]; then
      echo "MISSING_FOCUS $id $focus_path"
      errors=$((errors + 1))
    fi
  done < <(awk -F '\t' -v id="$id" '$1 == id {print $2}' "$FOCUS")
done < <(tail -n +2 "$MANIFEST")

if [[ "$errors" -ne 0 ]]; then
  echo "Verification failed with $errors structural error group(s)." >&2
  exit 1
fi

echo "Verification pass complete."
