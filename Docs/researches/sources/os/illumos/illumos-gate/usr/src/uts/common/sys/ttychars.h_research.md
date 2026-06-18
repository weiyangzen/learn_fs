# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttychars.h

## Purpose
Default legacy tty special character definitions.

## Main Interfaces
- Defines `struct ttychars` with erase, kill, interrupt, quit, start/stop, EOF, break, suspend, delayed suspend, reprint, flush, word erase, literal-next, and status characters.
- Defines `CTRL(c)` and defaults such as `CERASE`, `CKILL`, `CINTR`, `CQUIT`, `CSTART`, `CSTOP`, `CEOF`, `CBRK`, `CSUSP`, `CDSUSP`, `CRPRNT`, `CFLUSH`, `CWERASE`, `CLNEXT`, and `CSTATUS`.

## Dependencies And Relationships
Used by legacy terminal code and compatibility layers that need old default control-character values.

## Research Notes
The constants are historical defaults and should not be confused with modern termios configurable indexes.
