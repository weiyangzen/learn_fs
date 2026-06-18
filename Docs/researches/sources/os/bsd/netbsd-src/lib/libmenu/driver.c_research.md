# File Research: sources/os/bsd/netbsd-src/lib/libmenu/driver.c

Implements `menu_driver()`, the main input dispatcher for posted menus. It validates menu state, handles navigation requests, scrolling, first/last/next/previous item selection, toggle behavior, pattern clearing/backtracking, match cycling, printable-character pattern search, and user-command rejection.

Important dependencies: `<menu.h>`, `<ctype.h>`, `<stdlib.h>`, and `internals.h`.

Key behavior: it maintains `top_row`, current item, pattern buffer, and selection state; it calls `_menui_match_pattern()`, `_menui_draw_item()`, and `_menui_goto_item()` to update display and cursor state. `O_NONCYCLIC`, `O_RADIO`, `O_ONEVALUE`, `O_SELECTABLE`, and `O_SHOWMATCH` materially affect behavior.
