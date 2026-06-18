# sources/test-tools/kdevops/scripts/workflows/fstests/list_pids.sh

## Purpose
Lists fstests workflow processes that would be skipped or terminated by the fstests process killer.

## Important APIs and control flow
The file shares the process scanner with `kill_pids.sh` and switches to read-only mode because its basename is `list_pids.sh`. It filters by checkout path and matching fstests filesystem type, then prints command lines under "Would be skipped" or "Would be killed".

## State and dependencies
Read-only over process state and config files. Requires `/proc`, `ps`, `readlink`, `.config`, and `scripts/lib.sh`.

## Integration points
Used as a preflight and diagnostic tool before terminating an fstests workflow.

## Risks and test signals
It exposes the exact string-matching behavior of the killer, including broad process matches. Test while fstests is active and ensure unrelated checkouts or different filesystem configurations are not listed.
