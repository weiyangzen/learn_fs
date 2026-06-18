# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_subr.c

Implements core NILFS helper logic for block translation, segment-log reading, super-root discovery, raw node lifecycle, and directory lookup support.

Key points:
- Provides segment arithmetic helpers, metadata-file layout calculations, and a local little-endian CRC32 routine.
- `nilfs_bread()` maps logical file blocks through the NILFS btree, then special-cases metadata/system nodes by translating virtual blocks to physical device blocks through DAT.
- Btree lookup supports direct small maps and large btree maps, including recursive lookup through non-root btree nodes.
- `nilfs_mdt_trans()` maps metadata indexes into metadata-file block/entry locations; `nilfs_nvtop()` resolves virtual-to-physical blocks, with DAT itself treated as physically mapped.
- Mount recovery helpers scan segment summaries from the last partial segment, load/CRC-check super roots, and update in-memory superblock last-segment fields.
- Node allocation initializes `nilfs_node` locks and links to `nilfs_device` / `nilfs_mount`; disposal purges dirhash and destroys synchronization primitives.
- Directory lookup is backed by NetBSD `dirhash`: `dirhash_fill()` walks NILFS directory records, while `nilfs_lookup_name_in_dir()` verifies hash hits against disk directory entries.
- Mutation helpers are effectively read-only: update, resize, create, attach, and detach paths return `EROFS`; delete is empty.

Dependencies and interactions:
- Uses `nilfs_bswap.h` accessors for on-disk endian conversion.
- Reads through `bread()` on either `devvp` or the file vnode.
- Called by NILFS VFS mount code for super-root recovery and by vnode ops for lookup, bmap, strategy, and directory operations.

Risk/notes:
- The file is central to the read-only behavior of this NILFS implementation.
- Write/update hooks are placeholders; vnode operations that route here cannot persist changes.
