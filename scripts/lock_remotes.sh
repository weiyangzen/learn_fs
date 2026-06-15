#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/manifests/sources.tsv"
OUT="$ROOT/metrics/remotes/remotes.lock.tsv"

mkdir -p "$(dirname "$OUT")"
printf "tier\tcategory\tid\tpath\turl\tlocal_head\tremote_head\tstatus\n" > "$OUT"

tail -n +2 "$MANIFEST" |
while IFS=$'\t' read -r tier category id path url recurse default_count notes; do
  [[ -n "${tier:-}" ]] || continue
  local_head=""
  if [[ -d "$ROOT/$path/.git" ]]; then
    local_head="$(git -C "$ROOT/$path" rev-parse HEAD 2>/dev/null || true)"
  fi

  remote_head=""
  status="OK"
  if ! remote_head="$(GIT_TERMINAL_PROMPT=0 git \
    -c protocol.version=2 \
    -c http.lowSpeedLimit=1 \
    -c http.lowSpeedTime=20 \
    ls-remote "$url" HEAD 2>/dev/null | awk '{print $1; exit}')"; then
    status="REMOTE_UNREACHABLE"
  fi
  if [[ -z "$remote_head" && "$status" == "OK" ]]; then
    status="NO_REMOTE_HEAD"
  fi

  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$tier" "$category" "$id" "$path" "$url" "$local_head" "$remote_head" "$status" >> "$OUT"
done

echo "Wrote $OUT"
