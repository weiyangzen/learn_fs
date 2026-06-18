# File Research: sources/os/bsd/openbsd-src/sbin/ttyflags/ttyflags.c

Utility that applies or prints device-specific tty flags based on `/etc/ttys`.

Options:
- `-a`: process all `/etc/ttys` entries.
- `-p`: print current kernel tty flags instead of setting configured ones.
- `-v`: verbose warnings/output.
- `-n`: undocumented dry-run/no-op after computing target flags.

Behavior:
- Opens `/etc/ttys` with `setttyent()`.
- `all()` skips network pseudo-tty entries and applies each real tty.
- `ttys()` applies named tty entries.
- `ttyflags()` maps ttyent status flags to ioctl flags:
  - `TTY_LOCAL` -> `TIOCFLAG_CLOCAL`
  - `TTY_RTSCTS` -> `TIOCFLAG_CRTSCTS`
  - `TTY_SOFTCAR` -> `TIOCFLAG_SOFTCAR`
  - `TTY_MDMBUF` -> `TIOCFLAG_MDMBUF`
- Opens `/dev/<tty>` nonblocking and uses `TIOCSFLAGS` or `TIOCGFLAGS`.
- Suppresses some expected missing/non-tty errors unless verbose.

Filesystem/storage relevance:
- Not filesystem logic. It reads system configuration and mutates character-device tty flags through ioctls.
