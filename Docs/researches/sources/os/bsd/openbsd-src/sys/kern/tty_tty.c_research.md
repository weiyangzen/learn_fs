# File Research: sources/os/bsd/openbsd-src/sys/kern/tty_tty.c

Controlling-terminal indirect device driver.

This file implements `/dev/tty` style operations by resolving the current process's controlling terminal vnode from the session and forwarding operations to that vnode. `cttyopen()`, `cttyread()`, and `cttywrite()` check for a controlling terminal, take an exclusive vnode lock, call the corresponding VOP operation with `NOCRED`, and unlock. Missing controlling terminals return `ENXIO` for open and `EIO` for read/write.

`cttyioctl()` handles controlling-terminal-specific requests before delegating to `VOP_IOCTL()`. `TIOCNOTTY` clears `PS_CONTROLT` for non-session leaders but rejects session leaders. `TIOCSCTTY` is rejected. The `TIOCSETVERAUTH`, `TIOCCLRVERAUTH`, and `TIOCCHKVERAUTH` cases manage session-level verified-authentication state, including root-only setup, a 1..3600 second timeout, and checks that compare real uid and parent pid.

`cttykqfilter()` forwards kqueue filters to the controlling tty vnode. If no controlling terminal exists, poll/select filters get `seltrue_kqfilter()` so polling can report readiness-like behavior, while other filters fail with `ENXIO`.

Notable constraints: operations use `NOCRED` because this is an indirection to an already-associated controlling terminal; verauth's uid/ppid checks are explicitly documented as imperfect; and session-leader semantics prevent `TIOCNOTTY` from detaching a controlling terminal through this path.
