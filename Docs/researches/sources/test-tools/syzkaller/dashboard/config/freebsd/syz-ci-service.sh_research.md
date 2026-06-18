# sources/test-tools/syzkaller/dashboard/config/freebsd/syz-ci-service.sh

Purpose: FreeBSD rc.d service wrapper for running `syz-ci` at boot.

Important APIs and variables: rc.d metadata `PROVIDE: syz_ci`, `REQUIRE: LOGIN`, `/etc/rc.subr`, variables `command`, `name`, `pidfile`, `rcvar`, `start_cmd`, `stop_cmd`, and configurable rc.conf variables `syz_ci_enable`, `syz_ci_chdir`, `syz_ci_flags`, `syz_ci_log`, and `syz_ci_path`.

Control flow: `syz_ci_start` changes to the configured working directory and launches `syz-ci` under `daemon -f`, redirecting output to the configured log and writing a pidfile. `syz_ci_stop` reads the pidfile, sends `SIGINT`, and waits up to 120 seconds with `pwait`. The script loads rc config and dispatches `run_rc_command "$1"`.

State and persistence: persistent state is the pidfile under `/var/run` and the configured syz-ci log. The service itself does not manage syz-ci state files.

Dependencies and integration points: FreeBSD rc system, `daemon`, `pwait`, `/usr/local/bin` in PATH for Go, an installed syz-ci binary, and rc.conf setup documented in comments.

Risks: `stop` assumes pidfile exists and contains a valid pid; missing/stale pidfiles may produce confusing failures. Variables are not always quoted in command arguments. The service uses `daemon -f`, so supervision semantics depend on FreeBSD daemon behavior and syz-ci signal handling.

Test signals: no automated tests. Operational validation is `service syz_ci start`, pidfile creation, log writes, and graceful `service syz_ci stop`.
