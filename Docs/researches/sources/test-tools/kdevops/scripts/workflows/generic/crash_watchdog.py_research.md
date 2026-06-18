# sources/test-tools/kdevops/scripts/workflows/generic/crash_watchdog.py

## Purpose
CLI wrapper around `KernelCrashWatchdog` for detecting kernel crashes/warnings on one host or all active hosts and optionally resetting affected guests.

## Important APIs
`get_active_hosts()` uses `ansible-inventory -i hosts --list` and returns baseline hosts. `run_crash_watchdog_on_host(args, host)` constructs `KernelCrashWatchdog` and returns crash/warning status. `run_crash_watchdog_all_hosts(args)` loops over active hosts. `write_log_section()` can embed log snippets, though it is not used by `main()`.

## Control flow
`main()` parses host, output directory, collection method (`auto`, `remote`, `console`, `ssh`), full-log mode, decode/reset toggles, fstests-log extraction, and warning saving. If invoked as `get_console.py`, it adjusts options for console retrieval. It exits 1 when any crash is detected and 0 otherwise.

## State and dependencies
May write crash/warning files, decode stack traces, and reset hosts through the library. Depends on Ansible, PyYAML, SSH, journal access, and `lib.crash`.

## Risks and test signals
`--save-warnings` is declared as an option with a default `True` string rather than a boolean action, so CLI semantics are confusing. It can reset guests as part of a status run. Test with `--no-reset`, each collection method, single-host and all-host modes.
