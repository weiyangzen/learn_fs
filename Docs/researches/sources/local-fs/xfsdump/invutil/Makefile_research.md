# File Research: sources/local-fs/xfsdump/invutil/Makefile

Builds the `xfsinvutil` inventory maintenance utility.

Key contents:
- Includes top-level xfsdump build definitions.
- Symlinks common headers/sources from `../common` and inventory headers/sources from `../inventory`.
- Always includes `invutil.c`; conditionally includes curses UI sources when `ENABLE_CURSES=yes`.
- Curses sources include `cmenu.c`, `fstab.c`, `invidx.c`, `list.c`, `menu.c`, `screen.c`, and `stobj.c`.
- Links with `LIBUUID` and `LIBCURSES`.
- Installs the command into `$(PKG_SBIN_DIR)`.

Notable observations:
- `LCFLAGS = -DDUMP` is always set; `-DHAVE_CURSES` is added only for curses builds.
- When curses is disabled, UI sources are still listed as source files but not compiled into the command.
