# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_bmap.c

## Scope

Implements ULFS logical-to-physical block mapping for LFS inodes, including direct blocks, single/double/triple indirect traversal, run-length discovery, and indirect logical block path construction.

## APIs And Behavior

- `ulfs_bmap()` returns the backing device vnode and maps one logical block through `ulfs_bmaparray()`.
- `ulfs_bmaparray()` handles direct block pointers for ULFS1/ULFS2, byte-swapping, `UNWRITTEN` sign-extension quirks, snapshot sentinel handling, holes, optional sequential run calculation, and indirect block lookup through cached or read indirect blocks.
- `ulfs_getlbns()` computes the chain of negative logical metadata block numbers and offsets needed to reach a data or indirect block.

## State And Dependencies

The mapper uses dinode direct/indirect arrays, `struct ulfsmount` geometry, LFS block-pointer conversion, buffer cache `getblk`/`incore`, `VOP_STRATEGY`, and `ulfs_bswap.h` helpers. The caller can provide a custom sequential predicate; LFS page writing uses a hole-oriented predicate while ordinary ULFS mapping uses physical adjacency.

## Risks And Invariants

The code must preserve the special `UNWRITTEN == -2` value when reading 32-bit pointers into wider values. Holes map to `-1` for ordinary files but snapshot files can map holes/sentinel values specially. Indirect block logical numbering is negative and formula-sensitive; incorrect `ulfs_getlbns()` paths would corrupt metadata reads and allocation.
