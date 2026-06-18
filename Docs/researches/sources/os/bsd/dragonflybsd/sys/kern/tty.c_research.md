# File Research: sources/os/bsd/dragonflybsd/sys/kern/tty.c

## Summary
Core DragonFly BSD terminal line-discipline implementation. It manages tty lifetime, canonical/raw input processing, output translation, termios ioctls, job-control signaling, flow control, kqueue readiness, tty sleep/revoke handling, and exported tty statistics.

## Main Responsibilities
- Opens, closes, initializes, registers, unregisters, and revokes `struct tty` objects.
- Implements default termios line discipline: `ttyinput`, `ttread`, `ttwrite`, `ttioctl`, `ttylclose`, `ttymodem`.
- Maintains tty input/output queues through `clist` helpers and speed-derived watermarks.
- Handles canonical editing: erase, kill, word erase, reprint, literal-next, EOF/EOL delimiters, echo, `PENDIN`, and `EXTPROC`.
- Handles signals and job control: `VINTR`, `VQUIT`, `VSUSP`, `VDSUSP`, `VSTATUS`, `VCHECKPT`, background read/write/ioctl checks, foreground process group changes.
- Supports tty wakeups, async `SIGIO`, kqueue read/write filters, and `kern.ttys` sysctl snapshots.

## Key APIs
- Lifecycle/session: `ttyopen`, `ttyclose`, `ttyclearsession`, `ttyclosesession`, `ttymalloc`, `ttyinit`, `ttyregister`, `ttyunregister`, `ttyrevoke`.
- Data path: `ttyinput`, `ttread`, `ttwrite`, `ttyread`, `ttywrite`, `ttyoutput`.
- Control path: `ttioctl`, `ttyflush`, `ttywait`, `ttyblock`, `ttstart`, `ttymodem`, `ttysleep`.
- Reporting/helpers: `ttyinfo`, `ttspeedtab`, `ttsetwater`, `termioschars`, `ttychars`, `tputchar`.

## Important Behavior
Most routines acquire `tp->t_token`; global tty registration uses `tty_token`. `ttyclose` frees clist buffers, bumps `t_gen`, resets line discipline to `TTYDISC`, and clears all tty state except registration.

Input processing enforces termios flags for break/parity handling, CR/LF mapping, IXON/IXOFF, canonical editing, signals, echoing, and queue overflow. Reads implement all noncanonical `VMIN`/`VTIME` combinations and return `ERESTART` from `ttysleep` if the tty generation changed while blocked.

`ttioctl` performs background `SIGTTOU` checks for mutating ioctls, controls exclusive mode, async ownership, virtual console selection, line discipline switching, termios updates, controlling-terminal setup, foreground pgrp assignment, window-size `SIGWINCH`, and drain timeout configuration.

## Risks
This file is a dense concurrency boundary: tty tokens, process tokens, pgrp/session references, vnode revocation, and sleep/restart semantics interact. Queue sizing depends on speed/watermark calculations and clist allocation. Several comments identify legacy race or TODO areas around `IXOFF`, `PENDIN`, `EXTPROC`, and line-discipline transitions.
