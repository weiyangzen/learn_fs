# File Research: sources/os/bsd/freebsd-src/sbin/init/init.c

## Purpose
Implements FreeBSD `init(8)`, PID 1. It is the system bootstrap and lifecycle state machine: single-user mode, `/etc/rc`, multi-user getty supervision, shutdown, reboot, and reroot.

## Main Elements
- `main()` validates root/PID 1, handles SysV-compatible runlevel signals when enabled, parses `-d`, `-s`, `-f`, `-r`, installs signal handlers, closes standard fds, processes `kenv` overrides, optionally mounts `devfs`, and starts the state machine.
- State functions: `single_user`, `runcom`, `read_ttys`, `multi_user`, `clean_ttys`, `catatonia`, `death`, `death_single`, `reroot`, and `reroot_phase_two`.
- Signal-driven transitions map `SIGHUP`, `SIGINT`, `SIGEMT`, `SIGTERM`, `SIGTSTP`, `SIGUSR1`, `SIGUSR2`, and `SIGWINCH` to rescans, single-user, reroot, halt, reboot, poweroff, or login blocking.
- `/etc/ttys` processing builds `session_t` records, parses getty/window command arguments, starts gettys, restarts dead sessions, and removes changed/deleted sessions.
- Shutdown paths revoke ttys, run `/etc/rc.shutdown`, kill remaining processes with `SIGTERM`/`SIGKILL`, optionally run `/etc/rc.final`, sync, and call `reboot()`.
- Reroot copies the running init binary to tmpfs at `/dev/reroot/init`, execs that temporary init with `-r`, asks the kernel to mount the new root with `RB_REROOT`, then searches the new root for init.

## Dependencies And Integration
Uses FreeBSD kernel sysctls, `kenv`, boot/shutdown tracing, `nmount`, `reboot`, `libutil` login tty helpers, DB hash storage for pid-to-session lookup, `/etc/ttys`, `/etc/rc`, `/etc/rc.shutdown`, `/etc/rc.final`, and paths from `pathnames.h`.

## Risk Notes
This is critical PID 1 code. Errors can prevent boot, leave no login sessions, or interrupt shutdown. Reroot and shutdown are especially sensitive because they kill processes, revoke terminals, mount/unmount filesystems, and exec replacement init binaries.
