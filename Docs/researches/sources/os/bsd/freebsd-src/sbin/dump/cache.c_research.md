# File Research: sources/os/bsd/freebsd-src/sbin/dump/cache.c

## Purpose
Implements a simple read cache for `dump` filesystem block reads.

## Main Elements
- `Block`: cache entry with hash-chain pointer, block-aligned offset, and data pointer.
- Cache globals: `DataBase`, `BlockHash`, `BlockSize`, `HSize`, `NBlocks`.
- `cinit()`: derives cache block size from filesystem block size times `BLKFACTOR`, caps at `MAXBSIZE`, allocates block metadata/hash table, mmaps anonymous data backing, and initializes hash chains.
- `cread()`: cached `pread()` wrapper. It bypasses cache when disabled, filesystem block size unknown, request crosses cache block boundary, or request is at least a cache block. On miss, reuses the tail entry in the bucket chain, reads a full cache block, and moves hits/misses to the bucket head.

## Dependencies And Integration
Uses global `sblock` and `cachesize` from `dump.h`. Called by dump block/inode traversal code instead of direct `pread()` for small repeated filesystem metadata reads.

## Risk Notes
`HSize = NBlocks / HFACTOR`; very small cache sizes could produce zero hash size and bad modulo behavior. Allocation and `mmap` failures are not checked before use. Failed full-block reads fall back to direct `pread()`.
