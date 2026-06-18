# sources/test-tools/kdevops/scripts/workflows/fstests/fstests_watchdog.py

## Purpose
Reports fstests progress per host, detects stalls, and integrates crash detection/reset handling.

## Important APIs
`print_fstest_host_status(host, verbose, use_remote, use_ssh, basedir, config)` gathers kernel version, current/last test status, stall estimate, and crash state. `_main()` parses hostfile, section, verbosity, systemd-remote, and SSH forcing options.

## Control flow
The watchdog reads `.config`, optionally validates membership in `systemd-journal-remote`, enumerates hosts, prints a table, and processes each host. It prefers systemd-remote journal data when configured, falls back to SSH for kernel version and process discovery, computes progress from historical `check.time`, adjusts for soak-duration tests, then runs `KernelCrashWatchdog.check_and_reset_host()`.

## State and persistence
Reads host inventories, local config/results, remote journals/processes, and may write crash logs and reset hosts through the crash watchdog.

## Dependencies and integration
Depends on local `lib.kssh`, `lib.fstests`, `lib.systemd_remote`, and `lib.crash`, plus SSH, journal files, and group permissions.

## Risks and test signals
It can reset hosts during a status check if crashes are found. Group lookup uses `grp.getgrnam()` but assumes success path shape. Test with `--use-ssh`, systemd-remote enabled, active fstests, no running process, and known crash fixtures.
