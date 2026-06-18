# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttold.h

## Purpose
Legacy BSD/SVr3 terminal structure, ioctl, mode, and line discipline definitions.

## Main Interfaces
- Defines old terminal character structures `struct tchars`, `struct tc`, `struct sgttyb`, `struct ltchars`, and `struct winsize`.
- Defines old tty ioctl command base `tIOC` and commands such as `TIOCGETD`, `TIOCSETD`, `TIOCGETP`, `TIOCSETP`, `TIOCSETN`, `TIOCSETC`, `TIOCGETC`, `TIOCLBIS`, `TIOCLBIC`, `TIOCLSET`, `TIOCLGET`, `TIOCSBRK`, `TIOCCBRK`, `TIOCGWINSZ`, and `TIOCSWINSZ`.
- Defines old mode bits including hangup, tab expansion, lowercase simulation, echo, CR mapping, raw mode, parity, newline/tab/CR/VT/BS delays, tandem flow control, cbreak, local CRT erase modes, literal output, background stop, no-flush, and pass-8.
- Defines local mode aliases such as `LCRTBS`, `LPRTERA`, `LCRTERA`, `LMDMBUF`, `LLITOUT`, `LTOSTOP`, `LNOFLSH`.
- Defines line discipline constants `OTTYDISC`, `NETLDISC`, `NTTYDISC`, `TABLDISC`, `NTABLDISC`, `MOUSELDISC`, and `KBDLDISC`.

## Dependencies And Relationships
Used by tty compatibility code, especially `ttcompat.h`, to support programs using pre-termios terminal interfaces.

## Research Notes
This file preserves many obsolete constants. New code should use termios, but compatibility modules need these exact values.
