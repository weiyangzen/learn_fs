# sources/test-tools/kdevops/scripts/workflows/blktests/list_pids.sh

## Purpose
Lists, without killing, processes that the blktests workflow kill helper would skip or terminate.

## Important APIs and control flow
This file shares the same body as `kill_pids.sh` and switches behavior based on `CALL=$(basename $0)`. When invoked as `list_pids.sh`, it sets `LIST_ONLY=true`, scans same-checkout workflow processes, and prints "Would be killed" or "Would be skipped" with `/proc/<pid>/cmdline` contents.

## State and dependencies
Read-only except for sourced shell variables. Requires `/proc`, `ps`, `readlink`, grep tools, `TOPDIR/.config`, and `scripts/lib.sh`.

## Integration points
Primary safety companion before running `workflows/blktests/kill_pids.sh`.

## Risks and test signals
Because it uses the exact matching logic as the killer, list output is the best preflight signal. NUL-separated `/proc/<pid>/cmdline` may print densely. Test during an active blktests run and verify protected kernel CI/baseline loop entries are marked skipped.
