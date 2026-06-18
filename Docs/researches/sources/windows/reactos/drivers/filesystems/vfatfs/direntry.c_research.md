# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/direntry.c

Purpose: Provides read-side directory-entry manipulation for FAT/FAT32/FATX. It extracts first cluster values, tests whether directories are empty, and iterates directory entries while reconstructing VFAT long names.

Key routines:
- `vfatDirEntryGetFirstCluster` returns a full first-cluster number, combining high/low words for FAT32 and using FATX layout for FATX volumes.
- `FATIsDirectoryEmpty` and `FATXIsDirectoryEmpty` scan cached directory data and treat only end/deleted entries, skipping `.` and `..` for normal FAT non-root directories.
- `FATGetNextDirEntry` maps directory file pages, handles starting in the middle of long-name slot runs, reconstructs LFN entries, verifies alias checksums against the 8.3 entry, and falls back to short names when needed.
- `FATXGetNextDirEntry` scans FATX entries, synthesizes `.` and `..` for non-root directories, and converts FATX OEM names to Unicode.

Implementation notes:
- Directory content is accessed through `vfatFCBInitializeCacheFromVolume` and cache manager calls (`CcMapData`, `CcUnpinData`) instead of direct disk reads.
- FAT long-name reconstruction copies 13 UTF-16 characters per slot, uses the `0x40` final-slot marker to terminate, validates slot index bounds, tracks a slot bitmap, and checks the short-name checksum.
- Deleted entries reset accumulated long-name state. End entries terminate iteration with `STATUS_NO_MORE_ENTRIES`.
- FATX has one fixed-size entry per file and uses filename length/deleted markers rather than VFAT LFN slot chains.

Dependencies and interactions:
- Called through the `VFAT_DISPATCH` table initialized in `dirwr.c`.
- Feeds `FindFile`, FCB creation, directory query formatting, delete checks, and path resolution.

Notable limitations and risks:
- Some corruption cases are logged and skipped or converted to no-more-entries rather than surfaced as hard corruption errors.
- The FAT directory-size traversal assumes page-sized mapping windows and carefully remaps at page boundaries; bugs here would affect all path lookup and enumeration.
