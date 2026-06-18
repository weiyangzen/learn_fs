# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/fat.h

Defines FAT cluster constants, FAT type predicates, EOF detection, FAT operation flags, and internal FAT allocation/mapping prototypes.

Main responsibilities:
- Normalizes cluster marker values across FAT12, FAT16, and FAT32.
- Defines FAT masks and predicates for filesystem type checks.
- Declares cluster-chain mapping, allocation, freeing, extension, cache purge, and volume dirty-bit routines.

Key constants and macros:
- `MSDOSFSROOT` and `CLUST_FREE` are both zero in different contexts.
- `CLUST_FIRST` is the first allocatable cluster.
- `CLUST_RSRVD`, `CLUST_BAD`, `CLUST_EOFS`, and `CLUST_EOFE` represent reserved, bad, and EOF ranges.
- `FAT12_MASK`, `FAT16_MASK`, `FAT32_MASK` select valid cluster bits.
- `FAT12(pmp)`, `FAT16(pmp)`, `FAT32(pmp)` inspect `pm_fatmask`.
- `MSDOSFSEOF(pmp, cn)` detects EOF markers after mask normalization.
- `FAT_GET`, `FAT_SET`, and `FAT_GET_AND_SET` drive `fatentry()`.
- `DE_CLEAR` requests zeroing newly allocated clusters during extension.

Important dependencies:
- Prototypes depend on `struct denode` and `struct msdosfsmount`.
- Implemented mainly by `msdosfs_fat.c`.

Notable risks and edge cases:
- FAT12 packed 12-bit entries require special handling in implementation.
- Cluster zero has special meanings for root directory, empty file, and free FAT entry depending on context.
