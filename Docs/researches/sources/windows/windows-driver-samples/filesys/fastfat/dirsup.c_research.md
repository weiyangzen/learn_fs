# File Research: sources/windows/windows-driver-samples/filesys/fastfat/dirsup.c

## Scope And Role

`dirsup.c` implements active FAT directory-entry support for the FastFat sample filesystem. It owns allocation, deletion, lookup, construction, timestamp/size synchronization, long-file-name handling, volume-label lookup, free-dirent rescans, and small-directory defragmentation.

The file is in subset A through `sources/windows/windows-driver-samples`, and was read completely.

## Main Entry Points

- `FatCreateNewDirent`: allocates contiguous directory entries in a parent DCB.
- `FatInitializeDirectoryDirent`: creates initial `.` and `..` entries for a new directory.
- `FatTunnelFcbOrDcb`: stores disappearing names/timestamps in the tunnel cache.
- `FatDeleteDirent`: marks an FCB/DCB dirent run deleted and optionally deletes EAs.
- `FatLfnDirentExists`: probes for an existing long filename.
- `FatLocateDirent`: central directory scan and matching routine for short names, LFNs, wildcards, and volume-label matches.
- `FatLocateSimpleOemDirent`: simpler 8.3 lookup wrapper.
- `FatLocateVolumeLabel`: scans the root directory for the volume-label dirent.
- `FatGetDirentFromFcbOrDcb`: pins the on-disk dirent associated with an FCB/DCB.
- `FatIsDirectoryEmpty`: tests whether only exempt entries remain.
- `FatConstructDirent`: fills short dirent fields and optional LFN prefix entries.
- `FatConstructLabelDirent`: fills a volume-label dirent.
- `FatSetFileSizeInDirent` / `FatSetFileSizeInDirentNoRaise`: writes FCB file size back to disk dirent.
- `FatUpdateDirentFromFcb`: flushes handle-derived archive, size, write-time, and access-time changes to the dirent and reports notifications.
- `FatComputeLfnChecksum`: computes the VFAT LFN checksum over the 11-byte short name.
- `FatRescanDirectory`: rebuilds DCB dirent hints and allocation bitmap state.
- `FatDefragDirectory`: compacts used dirents before free/deleted dirents for small directories.

## Important Local Helpers And Macros

- `FatConstructDot`, `FatConstructDotDot`, and `FatConstructEndDirent` build special directory entries. FAT32 high-cluster fields are always assigned but remain zero for non-FAT32.
- `FatReadDirent` pages through a directory by VBO, unpinning old BCBs and reading the next page when crossing a page boundary.
- The disabled `FatIsLfnPairValid` block documents a stricter LFN/short-name pairing check that was not compiled because Win95 could create short names without `~`.

## Directory Allocation Model

`FatCreateNewDirent` uses `ParentDirectory->Specific.Dcb.UnusedDirentVbo`, `DeletedDirentHint`, and `FreeDirentBitmap` as its allocator state. Clear bits represent free/deleted entries and set bits represent allocated entries, matching use of `RtlFindClearBits` for allocation and `RtlSetBits` after allocation.

The allocation path:

1. Rescans the directory if hints are uninitialized or forced by `RescanDir`.
2. Uses `UnusedDirentVbo` when never-used space is still inside current allocation.
3. Otherwise searches the free bitmap from `DeletedDirentHint`.
4. For non-FAT32 fixed root directories, may call `FatDefragDirectory` when fragmentation prevents satisfying a contiguous request.
5. If no free run exists, expands non-root/FAT32-capable directories by touching a byte through `FatPrepareWriteDirectoryFile`.
6. Rejects non-FAT32 root growth and also caps FAT32 directories at 64K entries.
7. In Chicago/VFAT mode, deletes an immediately preceding orphan LFN when allocating a single short dirent to reduce accidental LFN pairing.
8. Verifies selected dirents are actually `NEVER_USED` or `DELETED`, then marks bitmap bits allocated and saves updated hints.

## Directory Lookup And LFN Semantics

`FatLocateDirent` is the file’s core scanner. It requires the caller to hold the parent directory resource or VCB resource because deletion can rewrite LFN runs concurrently. It walks dirents from a rounded VBO, stopping on match, EOF, end-of-directory marker, or no match.

Short-name matching supports wildcard and constant 8.3 paths through CCB templates. Volume-label entries are skipped unless `CCB_FLAG_MATCH_VOLUME_ID` is set. If requested, VFAT LFN entries are reconstructed from reverse ordinal records, requiring ordinal continuity, matching checksum, `MustBeZero == 0`, valid tail bytes, and adjacency to the following short dirent. The final reconstructed LFN is upcased only when needed and matched with `FsRtlIsNameInExpression` or `FsRtlAreNamesEqual`.

`FatLfnDirentExists` builds a CCB that skips short-name comparison and does a case-insensitive LFN search. `FatLocateSimpleOemDirent` converts an OEM name to 8.3 and delegates to `FatLocateDirent`.

## Mutation, Synchronization, And Cache Use

The file uses BCB pinning and dirtying throughout, with careful unpin in `finally` blocks. Directory deletion asserts the VCB is held exclusive, acquires the parent DCB resource exclusive to synchronize with enumeration, then marks each LFN and short dirent in the run deleted. If `DeleteEa` is true and the filesystem is not FAT32, it attempts `FatDeleteEa` but swallows expected FAT exceptions. It clears free-bitmap bits for the deleted run and updates `DeletedDirentHint`.

`FatUpdateDirentFromFcb` skips bad FCBs, the root directory, and write-protected volumes. It derives updates from `FileObject->Flags` and CCB user-set flags, sets the archive bit on modification, updates last-write time unless user-set, updates file size when `FO_FILE_SIZE_CHANGED`, and updates last-access date only once per local day in Chicago mode. It reports notify filters and avoids marking the volume dirty for access-time-only updates.

## Directory Defragmentation

`FatDefragDirectory` is guarded by an exclusive VCB assertion and only handles directories up to `0x40000` bytes. It forces wait/write-through behavior, acquires every open child FCB exclusively, enumerates valid entries with `FatLocateDirent`, records used runs in a large MCB, copies used and unused bytes into pool buffers, marks unused dirents deleted, writes used dirents first and deleted/free dirents after them, updates the free bitmap, flushes repinned BCBs, then relocates open child FCB dirent offsets by short-name lookup. If relocation or flushing fails, affected children are marked bad.

## Integration Points

This file integrates with:

- Cache manager and mapped data helpers: `FatReadDirectoryFile`, `FatPrepareWriteDirectoryFile`, `FatPinMappedData`, `FatSetDirtyBcb`, `FatUnpinBcb`, `FatUnpinRepinnedBcbs`.
- FCB/DCB/VCB locking and conditions.
- Name conversion/matching helpers: `FatStringTo8dot3`, `Fat8dot3ToString`, `FatIsNameInExpression`, `FsRtlAreNamesEqual`, `FsRtlIsNameInExpression`.
- Tunnel cache: `FsRtlAddToTunnelCache`, `FsRtlDeleteKeyFromTunnelCache`.
- EA support through `FatDeleteEa`.
- Notify support through `FatNotifyReportChange`.
- FAT time conversion helpers.

## Risks And Test Signals

The riskiest areas are LFN reconstruction/deletion races, bitmap hint correctness, small-root defragmentation, and timestamp/dirty-volume side effects. Tests should cover fragmented fixed root directories, orphaned LFN cleanup, deletion during enumeration, volume-label lookup/update, FAT32 versus FAT12/16 root behavior, 64K-entry cap enforcement, case-preserving short-name tunneling, and last-access updates across local-day boundaries.
