# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/rowlist.c

Linked-list storage for parsed Word table row metadata.

Key routines:
- `vDestroyRowInfoList()` frees the row list and resets iteration state.
- `vAdd2RowInfoList()` appends valid row blocks and clamps negative column widths to zero.
- `pGetNextRowInfoListItem()` returns rows sequentially during rendering.

Important behavior:
- Rows with invalid or identical start/end file offsets are ignored.
- The read cursor is initialized when the first row is added and advances monotonically.

Dependencies:
- `row_block_type`, `xmalloc`, `xfree`, table constants.

Research relevance:
- Bridges binary table-property parsing and table-aware rendering in `word2text.c`.
