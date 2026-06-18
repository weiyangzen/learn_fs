# File Research: sources/os/bsd/netbsd-src/lib/libmenu/Makefile

Builds NetBSD `libmenu`, linking against `libcurses`. Sources are `menu.c`, `item.c`, `userptr.c`, `internals.c`, `driver.c`, `post.c`, and `attributes.c`.

It installs public headers `menu.h` and `eti.h`, and wires many manual page links for menu/item attributes, hooks, options, posting, cursor movement, formatting, patterns, and user pointers.

Debug builds can be enabled with `DEBUG_MENUS`, adding `-g` and `-DDEBUG`.
