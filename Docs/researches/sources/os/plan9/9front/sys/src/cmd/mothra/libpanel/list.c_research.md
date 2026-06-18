# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/list.c

Implements a scrollable selectable text list.

Key behavior:
- Uses a generator callback to enumerate item strings and a hit callback for selection.
- Draws visible rows and highlights current selection.
- Mouse handling tracks row under cursor and invokes callback on release.
- Vertical scrolling updates `lo`, uses pixel copying for partial redraws, and updates attached scrollbars.
- Computes requested size from item widths unless fill/expand flags allow width flexibility.

Important dependencies: font/draw helpers, scrollbar linkage, generator callback.

Notable risks:
- List length is determined by repeatedly calling `gen` until nil.
- `sel` can be outside visible range and is only drawn when visible.
