# sources/test-tools/kdevops/scripts/workflows/lib/kssh.py

## Purpose
Provides SSH-based helpers for workflow watchdogs to query remote process, program, kernel, test, and time state.

## Important APIs and types
Exceptions: `KsshError`, `ExecutionError`, `TimeoutExpired`. Functions: `_check()`, `dir_exists(host, dirname)`, `first_process_name_pid(host, process_name)`, `prog_exists(host, prog)`, `get_uname(host)`, `get_test(host, suite)`, `get_last_fstest(host)`, `get_last_blktest(host)`, and `get_current_time(host)`.

## Control flow
Each helper runs an SSH command via `subprocess.Popen`, waits up to 120 seconds, and converts return codes/timeouts into booleans or sentinel strings such as `Timeout` and `Uname-issue`. `get_test()` chooses `journalctl -k -g` when available, otherwise `dmesg`, then extracts the last `run <suite> ... at ...` line.

## State and dependencies
No persistence. Requires SSH, sudo on targets for several commands, remote `ps`, `which`, `journalctl` or `dmesg`, and local subprocess support.

## Integration points
Used by fstests and blktests libraries and watchdog scripts.

## Risks and test signals
Commands are passed as argument lists containing shell metacharacters like `|`, so behavior depends on SSH joining remote command arguments as intended. `first_process_name_pid()` casts stdout to int and can fail if multiple lines leak through. Test against reachable, unreachable, and sudo-limited hosts.
