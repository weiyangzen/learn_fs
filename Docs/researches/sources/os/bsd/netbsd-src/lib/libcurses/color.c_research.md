# File Research: sources/os/bsd/netbsd-src/lib/libcurses/color.c

Read completely: 711 lines.

This file implements libcurses color support and terminal color output. Public functions include `has_colors`, `can_change_color`, `start_color`, `init_pair`, `pair_content`, `init_color`, `color_content`, `use_default_colors`, `assume_default_colors`, and `no_color_attributes`. Internal functions include `__set_color`, `__unset_color`, `__restore_colors`, and `__change_pair`.

Global state includes `__using_color`, `__do_color_init`, `__default_color`, and `__default_pair`. `start_color` validates terminal capability support, clamps `COLORS` and `COLOR_PAIRS`, resets terminal colors, classifies the terminal color model as ANSI, HP, Tektronix, or other, initializes default RGB values and pair tables, marks color as active, and updates all existing windows with the default color pair.

`init_pair` validates pair and color numbers, maps ANSI color ordering to older `set_foreground`/`set_background` ordering for `COLOR_OTHER`, stores pair values, and calls `__change_pair` when an existing pair changes. `__set_color` emits terminal sequences for the active pair and tracks `_cursesi_screen->curpair`; `__unset_color` emits `orig_pair`; `__change_pair` dirties cells using a changed pair or clears matching color bits on `curscr`.

Important interactions: tightly coupled to terminfo capabilities, `_cursesi_screen`, `curscr`, `__virtscr`, the screen window list, and attribute color-bit encoding from `curses.h`.

Reliability notes: HP and Tektronix paths are placeholders. `pair_content` accepts `pair == _cursesi_screen->COLOR_PAIRS` because it checks `>` rather than `>=`, while `init_pair` rejects that value. Color state is global to the current screen and must be initialized before pair/color content APIs are meaningful.
