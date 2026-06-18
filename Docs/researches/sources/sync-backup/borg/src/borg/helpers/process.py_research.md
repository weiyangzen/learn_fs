# sources/sync-backup/borg/src/borg/helpers/process.py

## Purpose
Process, daemonization, signal, subprocess, filter-pipeline, and recurring-thread utilities used by Borg commands and mount operations.

## Important APIs, Types, And Functions
Daemon helpers `_daemonize`, `daemonize`, and `daemonizing`; signal helpers `_ExitCodeException`, `SignalException`, `SigHup`, `SigTerm`, `signal_handler`, `raising_signal_handler`, `SigIntManager`, global `sig_int`, and `ignore_sigint`; subprocess helpers `popen_with_error_handling`, `is_terminal`, `prepare_subprocess_env`, and `create_filter_process`; background utility `ThreadRunner`.

## Control Flow
`_daemonize` double-forks, detaches, redirects stdio, and yields old/new process IDs. `daemonizing` keeps a foreground process alive until the background signals success/failure or times out, optionally logging return code. Signal contexts install and restore handlers. `SigIntManager` debounces first Ctrl-C for graceful cancellation and lets later interrupts raise. `create_filter_process` inserts one-way filter subprocesses for inbound or outbound streams and kills/waits/raises depending on Borg and filter success.

## State And Persistence
Process state changes are real: forks, session creation, cwd `/`, stdio fd changes, signal handlers, subprocesses, and thread lifecycle. `sig_int` holds global cancellation state. `prepare_subprocess_env` copies and sanitizes environment, removing `BORG_PASSPHRASE` and setting `BORG_VERSION`.

## Dependencies And Integration Points
Used by FUSE background mounts, remote/filter commands, archive import/export, top-level signal handling, and terminal-dependent output. Integrates with platform flags and helper exit codes.

## Risks And Edge Cases
Fork/daemon logic is POSIX-specific. Foreground/background signaling uses SIGHUP/SIGTERM and must not leave locks stale. Signal handlers raising exceptions can happen at arbitrary bytecode locations. `popen_with_error_handling` forbids shell mode and returns `None` on common creation failures. Filter subprocess deadlock avoidance assumes one-way communication.

## Test Signals
Existing process tests should cover environment sanitization, command splitting failures, missing executable/permission errors, signal context restoration, SIGINT debounce, filter process success/failure, terminal detection, `ThreadRunner` termination, and daemon behavior with careful subprocess isolation.
