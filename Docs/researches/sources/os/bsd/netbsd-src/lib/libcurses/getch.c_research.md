# File Research: sources/os/bsd/netbsd-src/lib/libcurses/getch.c

Read completely: 1013 lines.

This file implements narrow-character input, keypad sequence mapping, key definition toggles, pushback, escape delay, and resize-aware byte input. Public APIs include `getch`, `mvgetch`, `mvwgetch`, `wgetch`, `keyok`, `define_key`, `ungetch`, `has_key`, and `set_escdelay`; internal APIs include `_cursesi_free_keymap`, `__init_getch`, `__unget`, and `__fgetc_resize`.

The file defines a large terminfo-code to curses-key table, builds a trie-like `keymap_t` from terminal key sequences in `__init_getch`, and parses input through internal `inkey`. The parser handles normal, assembling, timeout, and backout states, inter-character delays based on `ESCDELAY`, disabled key leaves, custom key definitions, and returns either raw bytes or symbolic `KEY_*` values.

`wgetch` refreshes touched windows, moves the physical cursor when echoing and the logical cursor moved, handles pending resize events and unget data, manages cbreak/nodelay/timeout modes, optionally parses keypad sequences, restores termios, echoes ordinary characters, maps carriage return to newline under `nl`, and returns `ERR` for negative input.

Important interactions: shared with `get_wch.c` through `_cursesi_state`, `_cursesi_screen->base_keymap`, and `__unget`. It relies on `keymap.h`, terminfo string arrays, termios helpers, refresh/cursor movement, and resize signal state.

Reliability notes: `add_new_key` and allocation helpers call `exit` on allocation failure, not `ERR`. In `__unget`, the realloc-failure fallback uses pointer and byte counts inconsistently in `memmove`, advancing by `sizeof(wchar_t)` elements and copying only `unget_len - 1` bytes, which is suspicious for a `wchar_t` array.
