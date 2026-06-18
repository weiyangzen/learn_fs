# File Research: sources/local-fs/xfsprogs/repair/bmap_repair.h

## Purpose

`bmap_repair.h` declares the public entry point for rebuilding an inode fork block map.

## Public API

`rebuild_bmap` takes a mount, inode number, fork selector, expected extent count, caller-held inode buffer/dinode pointers, and dirty flag. It repairs the selected fork and returns updated buffer/dinode pointers because the transaction and inode loading path can release and reacquire the inode cluster buffer.

## Important Invariants

- `whichfork` must select a supported inode fork.
- The caller must be prepared for `ino_bpp` and `dinop` to be refreshed.
- The function coordinates with caller dirty state to persist dinode changes before libxfs inode loading.

## Research Notes

The header is intentionally narrow: all rebuild machinery is private to `bmap_repair.c`.
