#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/manifests/sources.tsv"
TIER="required"
DRY_RUN=0
JOBS=4

usage() {
  cat <<'EOF'
Usage: scripts/clone_sources.sh [--tier required|important|adjacent|all] [--dry-run] [--jobs N]

Clone source repositories listed in manifests/sources.tsv.

The default is --tier required. "important" clones required+important,
"adjacent" clones required+important+adjacent, and "all" is the same as
adjacent unless more tiers are added later.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tier)
      TIER="${2:?missing tier}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --jobs)
      JOBS="${2:?missing jobs}"
      shift 2
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

clone_one() {
  local tier="$1" id="$2" path="$3" url="$4" recurse="$5"
  local abs="$ROOT/$path"

  if [[ -d "$abs/.git" ]]; then
    echo "SKIP existing $id $path"
    return 0
  fi

  mkdir -p "$(dirname "$abs")"
  echo "CLONE $tier $id $url -> $path"
  if [[ "$DRY_RUN" == "1" ]]; then
    return 0
  fi

  local args=(clone --depth=1 --filter=blob:none)
  if [[ "$recurse" == "yes" ]]; then
    args+=(--recurse-submodules --shallow-submodules)
  fi
  args+=("$url" "$abs")
  git "${args[@]}"
}

export -f clone_one include_tier
export ROOT DRY_RUN
tmp_jobs="$(mktemp)"
trap 'rm -f "$tmp_jobs"' EXIT

while IFS=$'\t' read -r tier category id path url recurse default_count notes; do
  [[ -n "${tier:-}" ]] || continue
  if include_tier "$tier"; then
    printf "%s\t%s\t%s\t%s\t%s\n" "$tier" "$id" "$path" "$url" "$recurse" >> "$tmp_jobs"
  fi
done < <(tail -n +2 "$MANIFEST")

xargs -n 5 -P "$JOBS" bash -c 'clone_one "$@"' _ < "$tmp_jobs"

echo "Clone pass complete. Consider running scripts/lock_remotes.sh and scripts/verify_sources.sh."
