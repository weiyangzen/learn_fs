# File Research: sources/windows/reactos/drivers/filesystems/fastfat/dirsup.c

## Purpose

`dirsup.c` is the FAT directory-entry support layer. It allocates, initializes, locates, constructs, deletes, rescans, defragments, and updates FAT dirents. It also implements long-file-name parsing/construction, volume-label lookup/construction, directory emptiness checks, tunnel-cache support, and delayed on-disk metadata updates from FCB/FileObject state.

This is the lower-level companion to `dirctrl.c`: `dirctrl.c` asks for matching entries, while `dirsup.c` understands how FAT short dirents, LFN dirent chains, free/deleted entries, and directory bitmaps are represented on disk.

## Core Helpers and Macros

- `FatConstructDot`, `FatConstructDotDot`, and `FatConstructEndDirent` initialize special directory entries.
- `FatReadDirent` pins the page containing a directory entry and advances within page-sized mapped directory windows.
- `FatComputeLfnChecksum` implements the standard FAT LFN checksum over the 11-byte short name.
- `FatRescanDirectory` rebuilds `UnusedDirentVbo`, `DeletedDirentHint`, and `FreeDirentBitmap`.
- `FatDefragDirectory` compacts used dirents and groups free/deleted/orphaned entries at the end of a small directory.

## Allocation and Initialization

`FatCreateNewDirent` allocates contiguous dirent slots inside a parent directory. It first uses `UnusedDirentVbo` if possible, otherwise searches `FreeDirentBitmap` from `DeletedDirentHint`. For non-FAT32 root directories with fragmented free space, it may call `FatDefragDirectory` if the root directory is small enough.

If no slot exists, it grows the directory by preparing a write beyond current allocation, except for fixed-size FAT12/FAT16 roots or directories capped at 64K entries. It verifies that selected entries are actually never-used or deleted before marking the bitmap bits allocated.

In Chicago mode, when allocating a single dirent, it checks the preceding dirent for an orphaned LFN and marks it deleted to avoid accidental future LFN/short-name pairing.

`FatInitializeDirectoryDirent` turns a newly created file dirent into a directory by allocating the first two entries and constructing `.` and `..`. For FAT32 it fills high cluster fields as well.

## Deletion and Tunneling

`FatTunnelFcbOrDcb` handles name tunneling before names disappear. Directory deletion removes the directory key from the volume tunnel cache. File deletion converts the short OEM name to Unicode, repairs case according to NT byte lowercase flags, and adds short name, exact-case long name, opened-by-shortname status, and creation time to `FsRtlAddToTunnelCache`.

`FatDeleteDirent` marks the LFN chain and short dirent deleted. It requires the VCB to be held exclusive and acquires the parent DCB resource to synchronize with enumerators. It can delete OS/2 EA data for non-FAT32 entries, clears corresponding free-dirent bitmap bits, optionally preserves file size and first cluster in the deleted short dirent for undelete tools, and updates `DeletedDirentHint`.

## Lookup and Matching

`FatLocateDirent` is the main directory scanner. It walks dirents from a supplied VBO and returns the first undeleted matching entry, its BCB, byte offset, optional DOS-name match flag, and optional long/original long filename.

Its matching logic handles:

- End of directory and EOF.
- Deleted entries.
- Volume-label entries, unless `CCB_FLAG_MATCH_VOLUME_ID` is set.
- Chicago LFN chains with ordinal validation, checksum validation, tail `0xffff` validation, and maximum LFN dirent count checks.
- Short-name wildcard matching through `FatIsNameInExpression`.
- Fast constant 8.3 matching by comparing the 11-byte dirent name in word-sized chunks.
- LFN wildcard or equality matching after upcasing the disk LFN.

Malformed LFN chains are usually ignored, but a zero ordinal marked as last long entry is treated as corruption. Valid LFN state is reset when deleted entries or invalid continuations are encountered.

`FatLfnDirentExists` creates a temporary CCB that skips short-name comparison and uses mixed-case query behavior to search for a specific long name.

`FatLocateSimpleOemDirent` wraps `FatLocateDirent` for exact simple OEM 8.3 lookups without LFN handling. `FatLocateVolumeLabel` scans the root directory for a nondeleted volume-label dirent and pins it writable.

## Direct Dirent Access and Directory State

`FatGetDirentFromFcbOrDcb` reads and pins the short dirent identified by an FCB/DCB’s stored offset. It tolerates failure during removable-media verification when `ReturnOnFailure` is true, otherwise missing dirents raise corruption.

`FatIsDirectoryEmpty` scans after `.` and `..` for normal directories, or from zero for root, and treats deleted entries and LFNs as ignorable. Any live non-LFN dirent means the directory is not empty.

`FatRescanDirectory` walks a directory to rebuild free/allocated bitmap state. In this codebase, set bits represent allocated dirents and clear bits represent free/deleted slots. It finds the first never-used VBO, the first deleted hint, marks allocated runs set, free runs clear, and clears all entries after the never-used marker.

## Construction and Metadata Updates

`FatConstructDirent` fills a short dirent from an OEM name, optional LFN, attributes, case flags, and creation-time input. It can zero and initialize timestamps, uses current system time when needed, supports tunneled creation time, and sets `FAT_DIRENT_NT_BYTE_8_LOWER_CASE` / `FAT_DIRENT_NT_BYTE_3_LOWER_CASE`.

When an LFN is supplied, it writes the LFN entries immediately before the short dirent, computes the checksum, splits the Unicode name into 13-character LFN fragments, sets the final fragment’s last-entry bit, null terminator, and `0xffff` tail padding, and fills the standard LFN attribute/type/checksum fields.

`FatConstructLabelDirent` builds a volume-label dirent: zeroed record, padded 11-byte label, current FAT write time, volume-id attribute, no EA, and zero file size.

`FatSetFileSizeInDirent` and `FatSetFileSizeInDirentNoRaise` write an FCB file size into its dirent, with the latter swallowing expected exceptions.

`FatUpdateDirentFromFcb` flushes deferred file-object effects into the on-disk dirent. It may set archive bit, update last-write time, update file size, and in Chicago mode update last-access date only if the previous access day differs from the current local day. It reports notify changes and marks the BCB dirty, avoiding marking the volume dirty for access-time-only updates.

## Defragmentation

`FatDefragDirectory` is used when a small non-FAT32 root directory has enough free entries but not enough contiguous entries. It requires exclusive VCB ownership, forces wait/write-through, acquires all child FCB resources, builds a large MCB describing used dirent ranges including valid LFNs, copies used and unused ranges into separate buffers, marks all unused entries as deleted, writes used entries first and unused entries after them, flushes repinned BCBs, rebuilds the free bitmap, and updates open child FCB dirent offsets.

If the flush or relocation lookup fails, it marks child FCBs bad because their on-disk positions may no longer be reliable.

## State, Dependencies, and Side Effects

This file mutates on-disk directory contents, DCB free-dirent allocation hints, free-dirent bitmaps, FCB dirent offsets, FCB timestamps, dirent FAT flags, tunnel cache entries, notify state, and dirty BCB/volume state.

It depends on FAT cache helpers (`FatReadDirectoryFile`, `FatPrepareWriteDirectoryFile`, `FatPinMappedData`, `FatUnpinBcb`, `FatSetDirtyBcb`), name conversion helpers, FSRTL tunnel/cache/name-expression/Mcb APIs, EA deletion, notification reporting, time conversion routines, and FCB/DCB resource ordering.

## Correctness Notes and Risks

The most delicate code is LFN parsing and directory compaction. LFN chains are order-sensitive and checksum-sensitive, and scanner state must be reset on deleted or malformed entries to avoid false pairings. `FatCreateNewDirent` proactively deletes orphaned LFN entries before single-slot allocation for the same reason.

The bitmap convention is easy to misread: allocated dirents are represented by set bits, while free/deleted dirents are clear. Allocation sets bits; deletion clears bits; rescans and defrag must preserve that convention.

`FatDefragDirectory` changes physical dirent offsets and therefore must either update every open child FCB or mark affected FCBs bad. It also deliberately limits operation to small directories to avoid cache-manager view complications.

Deletion requires strong synchronization: VCB exclusive plus parent DCB resource, because enumeration code can otherwise observe a partially deleted LFN chain.

## Research Coverage

Read completely. Covered dirent allocation, directory initialization, tunneling, deletion, LFN existence and lookup, volume-label lookup, direct dirent access, emptiness checks, dirent/label construction, size/time updates, checksum logic, full directory rescan, and root-directory defragmentation.
