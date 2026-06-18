# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rcbag_btree.h

This header defines the rcbag in-memory btree format and API.

Format:
- `RCBAG_MAGIC` identifies in-memory btree blocks.
- `struct rcbag_key` contains start block and block count.
- `struct rcbag_rec` contains start block, block count, and refcount.
- Pointers are `__be64`.
- `RCBAG_BLOCK_LEN` uses CRC long-block header length.

Macros:
- `RCBAG_REC_ADDR`
- `RCBAG_KEY_ADDR`
- `RCBAG_PTR_ADDR`

These compute record/key/pointer addresses in btree blocks and are noted as also used by userspace.

API:
- max records, size, and max-level calculations,
- cursor cache lifecycle,
- in-memory cursor creation and tree initialization,
- lookup/get/update/insert helpers.

When in-memory btrees are disabled, init/destroy macros compile to harmless stubs.
