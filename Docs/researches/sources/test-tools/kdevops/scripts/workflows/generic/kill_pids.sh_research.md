# sources/test-tools/kdevops/scripts/workflows/generic/kill_pids.sh

## Purpose
Shared process killer for workflow directories, supporting fstests, blktests, and reboot-limit based on the script's parent directory.

## Important APIs
`usage()`, `parse_args()`, and `list_pid()` implement CLI behavior. `CALL=$(basename $0)` decides list-only versus kill mode. `TARGET_WORFKLOW="$(basename $(dirname $0))"` selects workflow-specific config matching.

## Control flow
After sourcing `TOPDIR/.config` and `scripts/lib.sh`, the script validates the selected workflow is enabled, scans the user's process table, filters to same checkout and workflow config, skips kernel CI and baseline loop commands, and sends SIGTERM/SIGALRM to matching Make, run_loop, ansible-playbook, and SSH commands.

## State and persistence
Touches `$MANUAL_KILL_NOTICE_FILE` for manual kill notification and removes it at completion. Mutates process state.

## Dependencies and integration
Depends on `/proc`, shell tools, and kdevops config. Workflow-specific copies/symlinks reuse this body.

## Risks and test signals
The variable name `TARGET_WORFKLOW` is misspelled but consistently used. String process matching is broad. Use list mode first and test in isolated runs.
