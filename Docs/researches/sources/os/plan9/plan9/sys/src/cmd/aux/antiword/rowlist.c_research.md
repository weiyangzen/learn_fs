# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/rowlist.c

This file manages a linked list of detected Word table-row records.

Key behavior:
- `vAdd2RowInfoList()` appends valid row ranges and copies the row layout.
- Rejects rows with invalid or equal start/end file offsets.
- Normalizes negative column widths to zero.
- `pGetNextRowInfoListItem()` iterates through rows in insertion order.
- `vDestroyRowInfoList()` frees the list and resets write/read cursors.

Important details:
- The read cursor is initialized to the first row when the first list member is added.

Filesystem relevance:
- Indirect: records file offsets for table rows discovered while parsing Word streams.
