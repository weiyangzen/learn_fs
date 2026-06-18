# File Research: sources/os/bsd/netbsd-src/lib/libcurses/delch.c

Read completely: 154 lines.

This file implements character deletion at the current cursor position: `delch`, `mvdelch`, `mvwdelch`, and `wdelch`.

In narrow builds, `wdelch` shifts the rest of the line left by `memcpy`, fills the last cell with the background character, marks it as background, sets attributes to background color or zero depending on `curscr`, and touches the affected line. In wide builds, it first normalizes deletion from a continuation cell back to the base cell, deletes the full display-width character, frees the deleted cell's nonspacing list, shifts following cells left, fills trailing cells with background data, copies background nonspacing characters, sets `wcols = 1`, touches the line, and synchronizes.

Important interactions: relies on `wmove`, `__touchline`, `__sync`, `_cursesi_copy_nsp`, and wide-cell `wcols` continuation conventions.

Reliability notes: wide deletion modifies and frees per-cell nonspacing lists manually. Failure while copying background nonspacing data can leave part of the line already shifted.
