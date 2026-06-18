# sources/test-tools/kdevops/scripts/workflows/fstests/kill_pids.sh

## Purpose
Kills kdevops processes associated with the fstests workflow in the current checkout and filesystem configuration.

## Important APIs and control flow
This is the shared workflow process killer. For `TARGET_WORFKLOW=fstests`, it requires `CONFIG_KDEVOPS_WORKFLOW_ENABLE_FSTESTS=y`, records `FS=$CONFIG_FSTESTS_FSTYP`, and only targets processes whose current working directory is `TOPDIR` and whose `.config` has the same `CONFIG_FSTESTS_FSTYP`.

## State and persistence
Creates `$MANUAL_KILL_NOTICE_FILE` for manual kills, removes it at the end, and sends termination/alarm signals to matching process groups and PIDs.

## Dependencies and integration
Depends on `/proc`, user process list, sourced `.config`, and `scripts/lib.sh`. It is used for manual or watchdog cleanup after stuck fstests runs.

## Risks and test signals
String matching may kill broad SSH or Make processes if they belong to the same checkout and filesystem workflow. Always compare with `workflows/fstests/list_pids.sh` output first. Successful cleanup should leave no matching run_loop, ansible-playbook, or workflow SSH processes.
