# File Research: sources/os/bsd/netbsd-src/lib/libcurses/background.c

Read completely: 352 lines.

This file implements narrow and wide background-character APIs: `bkgdset`, `bkgd`, `wbkgdset`, `wbkgd`, `getbkgd`, and the wide-character `bkgrndset`, `bkgrnd`, `getbkgrnd`, `wbkgrndset`, `wbkgrnd`, `wgetbkgrnd`. Non-wide builds provide stub wide APIs that return `ERR` or do nothing.

For narrow cells, `wbkgdset` updates `win->bch` and `win->battr`, adding `__default_color` when color is active and no color pair is supplied. `wbkgd` applies the new background across all window cells, replacing cells marked `CA_BACKGROUND`, merging attributes, resetting wide column width when enabled, and touching the window.

The wide path maintains `win->bnsp`, the linked list of nonspacing background characters. `wbkgrndset` rejects empty and multi-column base characters, copies the old background into an `__LDATA`, updates background base/nonspacing characters and attributes, compares old/new backgrounds with `_cursesi_celleq`, and rewrites existing background cells with `_cursesi_copy_wchar`.

Important interactions: wide behavior depends heavily on `_cursesi_copy_nsp`, `_cursesi_copy_wchar`, `_cursesi_celleq`, and `__cursesi_free_nsp` from `curses.c`. Color default behavior depends on `__using_color` and `__default_color`.

Reliability notes: `wbkgrndset` is `void` and can return early after allocation failure, potentially after partially changing the background list. Its correctness also depends on `_cursesi_copy_nsp` safely copying into cells that may have no existing nonspacing list.
