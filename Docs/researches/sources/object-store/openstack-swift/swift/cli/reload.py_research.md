# sources/object-store/openstack-swift/swift/cli/reload.py

## Purpose
`reload.py` provides a safe CLI for reloading Swift WSGI server managers with minimal client impact. It verifies that a supplied PID is a supported Swift server manager, checks the running command's configuration, sends `SIGUSR1`, and optionally waits for systemd-style readiness notifications.

## Important APIs, types, and functions
- `EXIT_BAD_PID`, `EXIT_RELOAD_FAILED`, and `EXIT_RELOAD_TIMEOUT` encode user, reload, and wait failures.
- `validate_manager_pid(pid)` reads `/proc/<pid>/cmdline`, checks the session id, validates that exactly one non-Python `swift-*` script is present, and rejects unsupported processes or worker PIDs.
- `main(args=None)` defines CLI parsing, calls config validation through `subprocess.check_call(cmd + ["--test-config"])`, sends `SIGUSR1`, and waits on `NotificationServer` unless `--no-wait` is used.

## Control flow
The command requires a PID and accepts either a numeric timeout or `--no-wait`, plus verbose output. PID validation fails with exit code 2 when `/proc` data is unavailable, the process is not a Swift WSGI server, the server type lacks config-check support, or the process is a worker rather than the manager session leader. After validation, the original process command line is reused with `--test-config`; any non-zero result aborts before signaling. In wait mode, `NotificationServer` is bound before `SIGUSR1` is sent so reload notifications are not missed. The loop reads newline-delimited notification records until `READY=1`; timeout maps to `128 + ETIMEDOUT`. In no-wait mode, the signal is sent and success is printed immediately.

## State and persistence behavior
The file does not persist Swift data. It observes Linux `/proc`, process sessions, and notification sockets, and it mutates process state by sending `SIGUSR1` to the manager. The config test may read service config and fail without changing the running process. Output and exit codes are the durable operational contract for automation.

## Dependencies and integration points
It depends on Linux `/proc`, POSIX process sessions/signals, `subprocess`, sockets, and `swift.common.utils.NotificationServer`. It integrates with server manager processes that understand `--test-config`, `SIGUSR1` seamless reload, and `READY=1`/`RELOADING=1`/`STOPPING=1` notifications.

## Risks and edge cases
The process detector assumes command-line entries include a `/bin/` Swift script and that the manager is its own session leader; unusual packaging or launch wrappers may be rejected. There is no fallback for non-Linux systems without `/proc`. Reusing the original command with `--test-config` can fail if the command line included flags that do not compose with the test option. If the notification socket cannot bind, the tool exits failed before signaling; if the process never emits `READY=1`, reload may have happened but the CLI reports timeout.

## Test signals
Tests should mock `/proc` reads, `os.getsid`, `subprocess.check_call`, `NotificationServer`, `os.kill`, socket timeout, and OSError binding failures. Important cases include worker PID rejection, unsupported script rejection, config-test failure before signal, `--no-wait` behavior, verbose notification output, and timeout exit code.
