# File Research: sources/os/bsd/netbsd-src/lib/libedit/tty.h

## Purpose
Internal tty portability and state header for libedit.

## Main Content
- Normalizes platform-specific terminal constants and aliases, including AIX, ISC, convex, SVR4, POSIX, HPUX, and missing termios flags.
- Defines default control characters such as `CINTR`, `CQUIT`, `CERASE`, `CKILL`, `CEOF`, `CSTART`, `CSTOP`, `CSUSP`, and others.
- Defines internal control-character indexes `C_INTR` through `C_TIME`, plus `C_NCC` and `C_SH`.
- Defines mode indexes `EX_IO`, `ED_IO`, `TS_IO`, `QU_IO`, and flag categories `MD_INP`, `MD_OUT`, `MD_CTL`, `MD_LIN`, `MD_CHAR`.
- Defines `ttyperm_t`, `ttychar_t`, and `el_tty_t`.
- Declares tty lifecycle and mode-switch APIs.

## Integration
Included by libedit internals to embed tty state inside `EditLine` and to abstract differences across Unix tty implementations.

## Risks / Notes
The header encodes extensive legacy portability behavior. Any change to control-character indexes or mode constants must remain synchronized with `tty.c`.
