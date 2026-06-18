# File Research: sources/os/bsd/netbsd-src/sys/sys/ttychars.h

Read completely: 62 lines.

Compatibility header for old tty control characters.

Key elements:
- Defines `struct ttychars` with erase, kill, interrupt, quit, start/stop, EOF, break, suspend, delayed suspend, reprint, flush, word erase, and literal-next characters.
- If `USE_OLD_TTY` is defined, includes `ttydefaults.h` for default character constants.

Risks and notes:
- Historical compatibility interface; modern code should use `termios`.
- Structure layout may still matter to compatibility code.
