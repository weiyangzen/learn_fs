# File Research: sources/virtualization/libblockdev/src/plugins/fs/nilfs.h

Declares NILFS2 info data and operations.

Key contents:
- Defines `BDFSNILFS2Info` with `label`, `uuid`, `size`, `block_size`, and `free_blocks`.
- Declares copy/free helpers.
- Declares mkfs, label, UUID, info, and resize APIs.

Important invariants:
- Check and repair APIs are absent because NILFS2 support reports them unavailable.
- Returned info structs are caller-owned.

Filesystem/block relevance:
- Exposes NILFS2 filesystem management to generic dispatch and callers.

Notable risks:
- The API exposes total device size and free block count, but not a total block count field.
