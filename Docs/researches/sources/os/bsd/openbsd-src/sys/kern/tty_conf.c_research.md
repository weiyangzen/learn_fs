# File Research: sources/os/bsd/openbsd-src/sys/kern/tty_conf.c

Defines the kernel line-discipline switch table.

Contents:
- `linesw[]`: array of `struct linesw` entries for termios, defunct legacy disciplines, optional PPP, optional NMEA, optional MSTS, and optional EndRun.
- `nlinesw`: number of registered line disciplines.
- `nullioctl()`: discipline ioctl stub returning `-1` so generic tty ioctl handling can continue.

Behavior:
- The default discipline uses `ttyopen`, `ttylclose`, `ttread`, `ttwrite`, `ttyinput`, `ttstart`, and `ttymodem`.
- Disabled or defunct disciplines are wired to `enodev`/error stubs.
- Optional disciplines are included only when their config counts are nonzero.

Filesystem/storage relevance:
- Not filesystem logic. It is the dispatch table behind tty character-device behavior and determines which line-discipline methods handle reads, writes, input, close, and ioctl fallback.
