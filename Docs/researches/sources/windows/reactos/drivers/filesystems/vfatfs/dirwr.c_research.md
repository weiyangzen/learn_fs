# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/dirwr.c

Purpose: Implements write-side directory operations: directory cache setup, entry updates, add/delete/move/rename logic, free-slot discovery, and FAT/FATX dispatch table wiring.

Key routines:
- `vfatFCBInitializeCacheFromVolume` creates a stream file object for a directory FCB, attaches a CCB, initializes a cache map, grabs the FCB, and marks `FCB_CACHE_INITIALIZED`.
- `VfatUpdateEntry` pins the parent directory entry for an FCB and writes the current in-memory entry back to disk.
- `vfatRenameEntry` renames FATX entries in place but delegates normal FAT rename to `VfatMoveEntry` because long-name/short-name slot changes may be needed.
- `vfatFindDirSpace` scans for contiguous deleted/end slots, extends directories by one cluster when needed, and clears new/free separator entries.
- `FATAddEntry` creates FAT directory entries, generates DOS 8.3 aliases and VFAT LFN slots, allocates directory clusters for new directories, writes `.` and `..`, and constructs or updates the FCB.
- `FATXAddEntry` creates fixed FATX entries with up to 42 OEM bytes of filename data.
- `FATDelEntry` and `FATXDelEntry` mark entries deleted and, unless moving, free the file cluster chain.
- `VfatMoveEntry` deletes the old entry into a move context, re-adds under the target parent/name while preserving cluster/time/size, and flushes parent directory caches.

Implementation notes:
- Normal FAT long names use one or more LFN slots plus a short entry. Short-name generation uses `RtlIsNameLegalDOS8Dot3` and `RtlGenerate8dot3Name`, checking for collisions with `FindFile`.
- Creation timestamps are initialized from system time; moves preserve creation time, file size, and first cluster.
- Directory creation allocates a first cluster, initializes cache for the new directory, zeroes the cluster, and writes `.`/`..` entries with parent cluster values.
- FAT32 free-cluster count is refreshed after cluster allocation/free in relevant paths.
- FATX root/non-root indices differ because FATX iteration synthesizes `.`/`..`; add/update logic adjusts indices accordingly.

Dependencies and interactions:
- Calls FAT-chain functions (`NextCluster`, `GetNextCluster`, `WriteCluster`, `FAT32UpdateFreeClustersCount`), FCB update/create helpers, cache manager pin/dirty APIs, and notification-adjacent FCB metadata update paths.
- Exports `FatDispatch` and `FatXDispatch` with empty-dir, add, delete, and get-next-entry function pointers.

Notable limitations and risks:
- Several comments say status checks are FIXME, especially around cluster-chain writes and FCB creation/update in FATX add.
- FAT rename is implemented as move/delete/re-add, which is correct for LFN slot reshaping but makes crash consistency dependent on flush ordering.
