# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/brel.h

Declares the block relocation table abstraction. A relocation entry maps an old block to a new block and records reference metadata describing whether the owner is a block reference or inode reference.

Key types:
- `struct ext2_block_relocate_entry`: new block, offset, flags, and owner union.
- `ext2_brel`: pointer to `struct ext2_block_relocation_table`.
- `struct ext2_block_relocation_table`: magic, name, iterator cursor, private data, and method table.

Operations:
- `put`, `get`
- `start_iter`, `next`
- `move`, `delete`
- `free`

Macros wrap method calls as `ext2fs_brel_put`, `ext2fs_brel_get`, etc.

The header declares `ext2fs_brel_memarray_create`, implemented in `brel_ma.c`.

Implementation notes:
- `RELOCATE_TYPE_REF` masks reference type bits.
- The abstraction is backend-oriented, but this group includes only the memory-array backend.
