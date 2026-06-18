# File Research: sources/os/bsd/netbsd-src/lib/libmenu/menu.h

Public libmenu header. It defines menu-driver request constants, option flags, `MENU_STR`, opaque typedefs for `MENU` and `ITEM`, `Menu_Hook`, and the full internal layouts of `struct __item` and `struct __menu`.

Important dependencies: `<curses.h>` and `<eti.h>`.

The header declares the public API for driving menus, posting/unposting, window/subwindow assignment, formatting, hooks, options, patterns, user pointers, items, selection, and cursor/top-row state. Because the structures are exposed, field layout is part of the practical ABI surface.
