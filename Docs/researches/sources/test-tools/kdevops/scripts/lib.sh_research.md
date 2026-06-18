# sources/test-tools/kdevops/scripts/lib.sh

## Purpose
This shell fragment centralizes common kdevops runtime variables for scripts and workflow watchdog helpers. It is meant to be sourced after `.config` has exported Kconfig-derived shell variables and after `TOPDIR` is available.

## Important APIs and state
It does not define functions. Its API is a set of exported or shell-global variables: `PLAYBOOKDIR`, `INVENTORY`, `KDEVOPSHOSTSPREFIX`, kernel CI status/log file names, KOTD log file names, manual kill notice path, and workflow `.begin` marker paths. When fstests is enabled it also derives `FSTYP` and `TEST_DEV` from `CONFIG_FSTESTS_*`.

## Control flow
Execution is immediate on source. It assigns variables and conditionally reads fstests settings if `CONFIG_KDEVOPS_WORKFLOW_ENABLE_FSTESTS=y`.

## Persistence and integration
The variables name persisted files under `TOPDIR`, including `.kernel-ci.*`, `.kotd.*`, `.running_kill_pids.sh`, and workflow begin markers. `workflows/*/kill_pids.sh` sources this file for `MANUAL_KILL_NOTICE_FILE`.

## Dependencies
Depends on `TOPDIR` and Kconfig variables already being in the environment or sourced shell.

## Risks and test signals
There is no validation for missing Kconfig variables, so unset values silently produce empty paths or settings. Test by sourcing it under a known `.config` and checking expected variables, and by running dependent kill/list scripts in list mode.
