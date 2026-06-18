# File Research: sources/os/bsd/openbsd-src/sbin/reboot/reboot.c

## Purpose

Implements `reboot` and `halt`, including shutdown logging, optional rc shutdown script execution, process termination, sync ordering, and final `reboot(2)` call.

## Main Behavior

The program checks its invocation name, setting halt mode and `RB_HALT` when invoked as `halt`. Options add dump, no-log, no-sync, powerdown for halt, and quick reboot flags. It requires effective root. Quick mode calls `reboot(howto)` immediately.

Normal mode logs the initiating user through syslog unless `-l` is used, records a wtmp shutdown entry, performs an early `sync()` unless `-n`, sends `SIGTSTP` to init, ignores SIGHUP and SIGPIPE, and runs `/etc/rc shutdown` on the console when present. If the rc script exits with status 2 during halt, powerdown is enabled.

After the point of no return, it blocks all signals, sends SIGTERM to all processes, waits while processes remain, syncs again unless disabled, sends repeated SIGKILL waves with increasing waits, then calls `reboot(howto)`. If process signaling fails unexpectedly, it attempts to restart init with SIGHUP and exits with an error.

## Platform Detail

When `CPU_LIDACTION` exists and powerdown is requested, it disables suspend-on-lid-close through `sysctl` before shutdown.

## Risks And Invariants

- `kill(-1, ...)` is used for broad process signaling; `ESRCH` is treated as success in single-user/exec cases.
- Init is stopped before rc shutdown and process killing; failure to stop init aborts.
- Signal blocking before final termination is intentional to guarantee progress to `reboot(2)`.
- `-p` is honored only when invoked as `halt`.
