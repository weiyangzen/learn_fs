# File Research: sources/os/bsd/netbsd-src/lib/libedit/config.h

This generated-style configuration header records platform feature availability for NetBSD libedit.

Defined features:
- `HAVE_CURSES_H`
- `HAVE_GETPW_R_POSIX`
- `HAVE_ISSETUGID`
- `HAVE_STRUCT_DIRENT_D_NAMLEN`
- `HAVE_SYS_CDEFS_H`
- `HAVE_TERMCAP_H`
- `HAVE_TERM_H`

Undefined/commented features:
- `HAVE_GETPW_R_DRAFT`
- `HAVE_NCURSES_H`

Integration:
- Includes `sys.h` after feature defines.
- Used by files like `filecomplete.c`, `el.c`, and tests to choose portable code paths.

Risks and notes:
- This is configuration glue, not runtime logic.
