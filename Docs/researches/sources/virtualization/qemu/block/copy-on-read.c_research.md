# File Research: sources/virtualization/qemu/block/copy-on-read.c

Implements the `copy-on-read` filter. It forwards most operations to its file child, but reads may set `BDRV_REQ_COPY_ON_READ` so data read from backing layers is materialized into the top node.

`cor_open()` opens the file child, sets supported flags, and optionally accepts a `bottom` node name. If `bottom` is provided, it validates that the node exists, is open, is not a filter, freezes the backing chain from this filter down to bottom, and holds a reference. Reads without a bottom simply forward with `BDRV_REQ_COPY_ON_READ`. Reads with a bottom iterate through allocation status, decide where copy-on-read is needed for ranges below the active layer, skip pure prefetch ranges that do not need read/write work, and forward partial requests.

Writes, zeroes, discards, compressed writes, eject, lock-medium, and getlength are pass-through operations. `cor_child_perm()` passes through consistent-read/write/resize permissions and requests `BLK_PERM_WRITE_UNCHANGED` unless inactive. `cor_close()` and `bdrv_cor_filter_drop()` unfreeze the backing chain and unref/drop the filter. The driver registers as filter `copy-on-read`.
