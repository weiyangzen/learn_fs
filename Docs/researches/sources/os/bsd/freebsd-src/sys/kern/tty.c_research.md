# File Research: sources/os/bsd/freebsd-src/sys/kern/tty.c

## Purpose
Core FreeBSD TTY framework. It provides character-device operations, TTY allocation/lifetime, termios state, controlling-terminal management, foreground/background job-control checks, `/dev/console`, `/dev/tty`-adjacent behavior, init/lock devices, sysctl listing, hooks, and DDB debugging.

## Main Structures and State
- Global `tty_list` plus `tty_list_sx` tracks all exposed TTYs for sysctl/debugging.
- Each `struct tty` owns termios state, input/output queues, condition variables, poll/kqueue state, flags, session/pgrp references, driver switch, softc, hook state, and optional custom mutex.
- `dev_console` and `dev_console_filename` implement `/dev/console` indirection.
- Tunables: `kern.tty_drainwait`, `security.bsd.allow_tiocsti`.

## Device Operations
- `ttydev_open()` serializes open/close, rejects gone devices, enforces callin/callout exclusion, exclusive mode, carrier wait, driver open, discipline open, and queue watermarks.
- `ttydev_close()` clears open flags, handles revoke cleanup, wakes blocked waiters, and delegates final teardown through `ttydev_leave()`.
- `ttydev_read()` and `ttydev_write()` call the line discipline while holding the TTY lock; writes serialize through `TF_BUSY_OUT` unless nonblocking.
- `ttydev_ioctl()` applies background job-control waits for mutating ioctls, applies init/lock termios masks, then calls `tty_ioctl()`.
- Poll and kqueue paths reflect line-discipline readability/writability and hangup/gone state.
- `ttydev_mmap()` delegates to the driver switch.

## Termios and Ioctls
- `tty_generic_ioctl()` handles modem bits, async owner, byte counts, termios get/set, line discipline query, pgrp/session ioctls, controlling TTY assignment/drop, flush/drain, console redirection, window size, exclusive mode, start/stop, status, and `TIOCSTI`.
- `tty_sti_check()` gates `TIOCSTI` with a global sysctl, privilege, read-open requirement, and controlling-terminal requirement.
- Termios changes filter unsupported flags, drain/flush for `TIOCSETAW/F`, call driver `param`, update queue watermarks, canonicalize input when needed, and notify PTY packet mode about start/stop settings.

## Lifetime and Device Nodes
- `tty_alloc_mutex()` patches missing driver callbacks with defaults, initializes termios, CVs, queues, kqueue lists, and locking.
- `tty_rel_free()` frees a TTY only after it is gone, unopened, hook-free, and no longer referenced by sessions.
- `tty_makedevf()` creates primary tty nodes, optional `.init`/`.lock` nodes, optional `cua*` callout nodes, sets ownership/modes, and inserts the TTY into `tty_list`.
- `tty_rel_gone()` simulates carrier loss, wakes waiters, marks `TF_GONE`, and attempts deferred free.

## Job Control and Sessions
- `tty_wait_background()` implements SIGTTIN/SIGTTOU background access semantics with orphaned pgrp and signal-mask handling.
- `TIOCSCTTY`, `TIOCNOTTY`, and `TIOCSPGRP` manipulate session and foreground process group state under `proctree_lock`.
- `tty_signal_sessleader()` and `tty_signal_pgrp()` send terminal-generated signals and clear stopped/flush-output state.

## Hooks and Console
- `ttyhook_register()` validates a file descriptor with `CAP_TTYHOOK`, verifies it references a tty cdev, attaches a hook, and updates bypass optimization.
- `ttyhook_unregister()` detaches and may trigger deferred free.
- `/dev/console` resolves the selected tty by name on open and logs console writes to the kernel message buffer.

## Diagnostics
- `kern.ttys` sysctl exports sanitized `xtty` records respecting visibility rules.
- Optional DDB commands show one tty or all ttys, including queue sizes, flags, termios, hooks, session/pgrp state, and driver callbacks.

## Notes and Risks
- Many operations intentionally drop and reacquire the TTY lock around allocations, user copies, ownership changes, and proctree operations.
- Correctness depends heavily on `TF_OPENCLOSE`, `TF_GONE`, `TF_ZOMBIE`, revoke counters, and condition-variable wakeups.
