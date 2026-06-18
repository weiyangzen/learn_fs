# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/dirhash.h

UFS directory hash structure and API header.

Key responsibilities:
- Documents and defines the hash-table scheme used to map filenames to directory offsets for large directories.
- Defines empty and deleted hash slot sentinels: `DIRHASH_EMPTY` and `DIRHASH_DEL`.
- Defines directory alignment and free-space-statistics sizing constants.
- Defines scoring constants for the dirhash cache eviction policy.
- Defines a two-level hash table layout through `DH_BLKOFFSHIFT`, `DH_NBLKOFF`, `DH_NBLKOFFMASK`, and `DH_ENTRY`.
- Defines `struct dirhash`, holding the hash arrays, free-space summaries, sequential-access optimization state, cache score, global-list membership, and TAILQ linkage.
- Declares dirhash lifecycle, lookup, free-space, add/remove/move, truncation, free, and checkblock functions.

Dependencies:
- Depends on `struct inode`, `struct direct`, `doff_t`, `TAILQ_ENTRY`, and directory constants from UFS headers.
- Implementations are elsewhere in the UFS codebase.

Notable risks:
- The header itself notes poor performance with the current lookup path for large directories.
- Open-addressing with spillover requires low utilization and correct `DIRHASH_DEL` handling to preserve chains.
- Free-space statistics assume `DIRBLKSIZ` is 512 bytes.
