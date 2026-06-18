# File Research: sources/os/bsd/netbsd-src/lib/libmenu/internals.c

Implements libmenu internal layout, matching, drawing, and navigation helpers. `_menui_stitch_items()` computes row/column placement and neighbors for every item; `_menui_calc_neighbours()` supports row-major/column-major and cyclic/noncyclic navigation; `_menui_goto_item()` updates current/top row and calls hooks; `_menui_match_pattern()` maintains incremental search state.

Important dependencies: `<menu.h>`, `<ctype.h>`, `<stdlib.h>`, `<string.h>`, and `internals.h`.

Drawing logic uses curses calls on `menu->scrwin`, applies foreground/grey/background attributes, renders mark/unmark strings, item names/descriptions, padding, visible flags, and cursor placement. Notable risk: `_menui_max_item_size()` only increases `max_item_width` and does not reset it before recomputing, so shrinking marks/options/items may leave stale larger widths.
