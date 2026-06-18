# File Research: sources/os/bsd/netbsd-src/sys/kern/tty_tty.c

## Purpose

`tty_tty.c` implements the indirect `/dev/tty` controlling-terminal character device. It forwards operations to the calling process's controlling terminal vnode.

## Main Responsibilities

- Resolves the current process's controlling tty vnode from session state.
- Forwards open, read, write, ioctl, poll, and kqueue filter operations.
- Implements `TIOCNOTTY` for non-session-leader callers.
- Rejects direct `TIOCSCTTY` through `/dev/tty`.

## Behavior

`cttyopen()` locks and opens the session's tty vnode if present. `cttyread()` and `cttywrite()` forward VOP reads/writes with `NOCRED`. `cttyioctl()` forwards most ioctls, clears `PL_CONTROLT` for non-session-leader `TIOCNOTTY`, and returns errors when no controlling tty exists.

`cttypoll()` returns `seltrue` if there is no controlling tty; otherwise it forwards to the underlying vnode. `cttykqfilter()` similarly attaches to the real vnode when available.

## Integration Notes

The exported `ctty_cdevsw` is a `D_TTY` character device wrapper and does not itself own a `struct tty`; it delegates through the session's vnode pointer.
