# File Research: sources/os/bsd/netbsd-src/lib/libcurses/attributes.c

Read completely: 491 lines.

This file implements libcurses attribute and color-pair state operations for `stdscr` and arbitrary `WINDOW` objects. Public wrappers include `attr_get`, `attr_on`, `attr_off`, `attr_set`, `color_set`, `attron`, `attroff`, `attrset`, `wattr_get`, `wattr_on`, `wattr_off`, `wattr_set`, `wcolor_set`, `getattrs`, `wattron`, `wattroff`, `wattrset`, `termattrs`, and, under wide-character support, `term_attrs`.

The implementation centralizes real mutation in `__wattr_on`, `__wattr_off`, and `__wcolor_set`. Those helpers validate `WINDOW *`, inspect the terminal capability table through `win->screen->term`, and only set attributes whose enter/exit terminfo sequences exist. Standout and underscore delegate to `wstandout`/`wunderscore` and `wstandend`/`wunderend`; color bits are carried in `__COLOR` and set only when the terminal reports colors.

Important interactions: this file depends on `curses.h` attribute masks, `curses_private.h` terminal accessors, global terminfo capability macros, and color globals such as `max_colors`. `wattr_set` deliberately replaces any color bits embedded in the requested attributes with `COLOR_PAIR(pair)`, matching ncurses behavior.

Reliability notes: most window-level helpers reject null windows, but `wattr_set` calls `__wattr_off` and `__wattr_on` without checking their return values and always returns `OK` if `opts == NULL`; a null `win` therefore yields `OK` despite failed internal operations. Attribute support is capability-gated, so callers cannot assume every requested bit is retained.
