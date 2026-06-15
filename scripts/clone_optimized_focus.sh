#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCES="$ROOT/manifests/sources.tsv"
TARGETS="$ROOT/manifests/research_targets.tsv"
FOCUS="$ROOT/manifests/focus_paths.tsv"
JOBS=2
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: scripts/clone_optimized_focus.sh [--dry-run] [--jobs N]

Clone only repositories marked optimized_count=yes in
manifests/research_targets.tsv, using shallow partial clone plus sparse
checkout of focus paths. This is the practical path for producing first-pass
LOC without cloning every large monorepo in full.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
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

clone_one() {
  local id="$1" path="$2" url="$3" recurse="$4"
  local abs="$ROOT/$path"
  local sparse_file
  sparse_file="$(mktemp)"

  awk -F '\t' -v id="$id" '$1 == id {print ($2 == "." ? "/*" : $2)}' "$FOCUS" > "$sparse_file"
  if [[ ! -s "$sparse_file" ]]; then
    printf "/*\n" > "$sparse_file"
  fi

  if [[ -d "$abs/.git" ]]; then
    echo "SKIP existing $id $path"
    rm -f "$sparse_file"
    return 0
  fi

  mkdir -p "$(dirname "$abs")"
  echo "SPARSE_CLONE $id $url -> $path"
  if [[ "$DRY_RUN" == "1" ]]; then
    sed 's/^/  focus /' "$sparse_file"
    rm -f "$sparse_file"
    return 0
  fi

  local args=(clone --depth=1 --filter=blob:none --sparse)
  args+=("$url" "$abs")
  GIT_TERMINAL_PROMPT=0 git "${args[@]}"
  git -C "$abs" sparse-checkout set --no-cone --stdin < "$sparse_file"
  rm -f "$sparse_file"
}

export -f clone_one
export ROOT FOCUS DRY_RUN

tmp_jobs="$(mktemp)"
trap 'rm -f "$tmp_jobs"' EXIT

awk -F '\t' 'NR > 1 && $6 == "yes" {print $1}' "$TARGETS" |
while IFS= read -r wanted_id; do
  awk -F '\t' -v wanted_id="$wanted_id" '
    NR > 1 && $3 == wanted_id {print $3 "\t" $4 "\t" $5 "\t" $6}
  ' "$SOURCES" >> "$tmp_jobs"
done

xargs -n 4 -P "$JOBS" bash -c 'clone_one "$@"' _ < "$tmp_jobs"

echo "Optimized sparse clone pass complete."
