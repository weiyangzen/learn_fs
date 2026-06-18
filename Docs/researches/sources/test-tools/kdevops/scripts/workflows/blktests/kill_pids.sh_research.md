# sources/test-tools/kdevops/scripts/workflows/blktests/kill_pids.sh

## Purpose
Kills kdevops workflow processes associated with the blktests workflow in the current checkout.

## Important APIs
Shared implementation with the workflow `list_pids.sh` wrappers. `usage()`, `parse_args()`, and `list_pid(pid, mode)` support `--help`, `--watchdog-mode`, list-only output, and manual-kill notice behavior.

## Control flow
The script sources `TOPDIR/.config` and `scripts/lib.sh`, identifies its target workflow from `basename $(dirname $0)`, verifies `CONFIG_KDEVOPS_WORKFLOW_ENABLE_BLKTESTS=y`, scans `ps -fu $USER`, filters processes whose `/proc/<pid>/cwd` is `TOPDIR` and whose `.config` matches the workflow, skips kernel CI and baseline loop processes, then sends signals to matching `make`, `run_loop`, `ansible-playbook`, and `ssh` processes.

## State and dependencies
Writes and removes `$MANUAL_KILL_NOTICE_FILE` unless in watchdog mode. Mutates process state by signaling process groups and processes. Depends on `/proc`, `ps`, `grep`, `readlink`, and sourced config.

## Risks and test signals
Process matching is string-based and can catch broad `ssh`/`make` processes in the checkout. Test with the sibling `list_pids.sh` first, then kill in a controlled workflow run.
