# File Research: sources/os/bsd/netbsd-src/lib/libcurses/acs.c

Read completely: 299 lines.

Initializes alternate character set tables for curses line-drawing and symbol characters. Global `_acs_char[]` stores narrow ACS mappings; with wide-character support, `_wacs_char[]` stores `cchar_t` mappings.

`__init_acs()` fills defaults, overlays terminal `acs_chars` pairs from terminfo, emits `ena_acs` if available, and snapshots the result into the `SCREEN`. `_cursesi_reset_acs()` restores globals from a `SCREEN`.

`__init_wacs()` initializes wide ACS defaults. In non-UTF-8 locales it uses character approximations; in UTF-8 it assigns Unicode box-drawing, arrows, bullets, math, and currency symbols and marks corresponding narrow ACS values with `__ACS_IS_WACS`. It then overlays terminfo ACS mappings as `WA_ALTCHARSET` entries. Risks are locale-sensitive behavior and global ACS state shared with screen snapshots.
