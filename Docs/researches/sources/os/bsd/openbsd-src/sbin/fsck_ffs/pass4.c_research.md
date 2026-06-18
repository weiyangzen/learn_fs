# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass4.c

## Scope

Phase 4 for `fsck_ffs`: resolves remaining inode reference-count problems, clears unreferenced files/directories, clears bad/duplicate inodes, and releases blocks no longer referenced.

## Main APIs

- `pass4()` iterates allocated inode-state tables and dispatches by inode state.
- `pass4check()` is an address callback that removes duplicate entries or clears block allocation bits.

## Control Flow

For `FSTATE` and `DFOUND`, nonzero remaining `ILNCOUNT()` values are corrected with `adjust()`. Zero-link inodes recorded in `zlnhead` are cleared as unreferenced. `DSTATE` directories are unreferenced and cleared. `DCLEAR` with zero size is cleared as zero-length; otherwise `DCLEAR` and `FCLEAR` are cleared as bad/duplicate. `USTATE` is ignored.

`pass4check()` walks each block fragment. Out-of-range blocks are skipped. Allocated blocks are compared against `duplist`; matching duplicate records are removed. If no duplicate record remains for a referenced block, the bit is cleared from `blockmap` and global used-block count decrements.

## Dependencies

- Uses `clri()`, `adjust()`, `ginode()`, `pass4check()` through `freeblk()`, and block-map helpers.
- Consumes `zlnhead` and `duplist` built in earlier phases.

## Risks And Edge Cases

- Duplicate list removal and block-map clearing happen per fragment, so partial fragments must stay consistent with `id_numfrags`.
- Zero-link processing mutates `zlnhead` by replacing found entries with the head value before freeing.
