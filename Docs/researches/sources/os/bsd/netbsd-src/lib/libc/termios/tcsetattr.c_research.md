# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcsetattr.c

## Purpose
Applies terminal attributes.

## Key Elements
If `TCSASOFT` is present, copies the termios and sets `CIGNORE`. Maps `TCSANOW`, `TCSADRAIN`, and `TCSAFLUSH` to `TIOCSETA`, `TIOCSETAW`, and `TIOCSETAF`.

## Dependencies
Uses `<sys/ioctl.h>`, `<termios.h>`, `_DIAGASSERT`, and `errno`.

## Behavior/Risks
Invalid option sets `EINVAL`. The `TCSASOFT` handling avoids changing hardware control bits via `CIGNORE`.
