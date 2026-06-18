# File Research: sources/os/bsd/netbsd-src/lib/libutil/pty.c

## Purpose
Allocates pseudo-terminals and forks child processes attached to them.

## Key Details
- `openpty` first tries `/dev/ptm` with `TIOCPTMGET`.
- Falls back to scanning legacy pty names.
- Sets slave ownership and mode using `tty` group when available.
- Applies optional termios and window size.
- `forkpty` opens a pty, forks, and in the child calls `login_tty(slave)`.

## Dependencies and Role
- Terminal/session utility.
