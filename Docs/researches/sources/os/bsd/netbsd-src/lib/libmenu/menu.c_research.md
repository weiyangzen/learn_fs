# File Research: sources/os/bsd/netbsd-src/lib/libmenu/menu.c

Implements menu-object APIs and the global `_menui_default_menu`. It manages marks/unmarks, windows/subwindows, format rows/columns, menu hooks, options, pattern setting, allocation/freeing, scaling, item-list attachment, top-row movement, and cursor positioning.

Important dependencies: `<ctype.h>`, `<menu.h>`, `<string.h>`, `<stdlib.h>`, and `internals.h`.

Key behavior: `new_menu()` copies default state and attaches items; `set_menu_items()` validates connection status, assigns parent/index fields, resets current/top row and pattern state, and recalculates neighbors; radio-style menus enforce at most one selected item. Notable risks: `free_menu()` frees `mark` but not `unmark`; `set_menu_items()` assumes `items` is non-NULL; `set_menu_pattern()` reallocates directly into `menu->pattern`, so failure can lose the previous pointer.
