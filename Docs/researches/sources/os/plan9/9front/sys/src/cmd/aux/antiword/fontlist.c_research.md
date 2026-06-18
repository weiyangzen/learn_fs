# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fontlist.c

This file stores extracted Word font runs in a linked list.

Key routines:
- `vDestroyFontInfoList()` frees all font run records and resets list state.
- `vCorrectFontValues(...)` normalizes font size/style: small caps become smaller capitals, superscript/subscript shrink size, size is clamped, and white text is remapped to light gray.
- `vAdd2FontInfoList(...)` appends a font block unless the offset is invalid; consecutive records at the same offset collapse to the last one.
- `pGetNextFontInfoListItem(...)` iterates records by recovering the containing list node from the embedded `font_block_type`.

Important behavior:
- Uses `FC_INVALID` to suppress impossible/past-end offsets.
- Maintains append order through `pAnchor` and `pFontLast`.
- Iterator exposes only `font_block_type`, hiding storage internals.

Dependencies:
- Font-style bit helpers, min/max/default font size constants, allocation helpers, and `offsetof`.

Role in antiword:
- Captures font transitions used later by layout, font-table minimization, and rendering.
