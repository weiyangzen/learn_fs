# File Research: sources/virtualization/qemu/block/snapshot-access.c

Implements the `snapshot-access` block driver, a read-oriented wrapper exposing a child's snapshot-access APIs. It opens a primary data child named `file`, mirrors its total sectors, refreshes its filename from the child, and registers as format `snapshot-access`.

Reads call `bdrv_co_preadv_snapshot()` and reject nonzero request flags with `-ENOTSUP`. Block status delegates to `bdrv_co_snapshot_block_status()`, and discard delegates to `bdrv_co_pdiscard_snapshot()`. Writes and write-zeroes are unsupported.

The child permission function requests no permissions and shares all permissions, relying on the child providing snapshot-access operations rather than normal write/read ownership. This makes the node a narrow adapter for accessing snapshot state rather than a general-purpose block filter.
