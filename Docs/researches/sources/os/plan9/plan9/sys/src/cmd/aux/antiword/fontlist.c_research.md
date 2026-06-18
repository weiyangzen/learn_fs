# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fontlist.c

Maintains an ordered linked list of Word font-change records.

Key structure:

- private `font_mem_type`, wrapping `font_block_type tInfo` plus `pNext`.

Key functions:

- `vDestroyFontInfoList()` frees the linked list and resets anchors.
- `vCorrectFontValues()` normalizes font records:
  - small caps become capitals at 4/5 size,
  - super/subscript become 2/3 size,
  - size is clamped to `MIN_FONT_SIZE..MAX_FONT_SIZE`,
  - Word white color `8` becomes light gray `16`.
- `vAdd2FontInfoList()` skips invalid offsets, replaces a consecutive record with the same file offset, normalizes values, and appends.
- `pGetNextFontInfoListItem()` exposes iteration over `font_block_type` while hiding the list node layout via `offsetof`.

This file is shared state for later output layout and font table pruning. It depends on `antiword.h` memory helpers like `xmalloc`, `xfree`, and `fail`.
