# File Research: sources/windows/reactos/drivers/filesystems/fastfat/allocsup.c

## Purpose

`allocsup.c` implements FastFAT allocation support: FAT scanning, free-space bitmap setup, cluster allocation/deallocation, file allocation lookup, MCB maintenance, FAT entry reads/writes, bad cluster tracking, FAT32 windowing, and dirty FAT tracking.

## Main Responsibilities

- Derive volume allocation geometry from the BPB.
- Build and maintain free-cluster bitmaps.
- Support FAT12, FAT16, and FAT32 entry formats.
- Split FAT32 free-space tracking into windows when the volume is too large for one bitmap.
- Map file VBOs to LBOs by combining cached MCB runs with on-disk FAT chain traversal.
- Allocate, extend, truncate, merge, split, and deallocate cluster chains.
- Keep FAT contents, in-memory MCBs, free-cluster counts, dirty FAT ranges, and dirent first-cluster fields coherent.
- Mark bad clusters in `BadBlockMcb`.
- Handle maximal 32-bit FAT file-size edge cases.

## Core Data Structures and Macros

- `FreeClusterBitMap`: RTL bitmap for the current allocation window.
- `FAT_WINDOW`: tracks `FirstCluster`, `LastCluster`, and `ClustersFree`.
- `MAX_CLUSTER_BITMAP_SIZE`: caps a bitmap window at 65536 clusters.
- `FatWindowOfCluster`: maps a cluster number to its FAT32 window.
- `DirtyFatMcb`: records dirty FAT sectors for later mirroring/flush behavior.
- Allocation macros wrap common operations:
  - `FatReserveClusters` sets bitmap bits and advances `ClusterHint`.
  - `FatUnreserveClusters` clears bits and may move `ClusterHint` backward.
  - `FatAllocateClusters` writes FAT links or last markers.
  - `FatFreeClusters` writes available markers.
  - `FatFindFreeClusterRun` optimizes single-cluster lookup before using `RtlFindClearBits`.

## Key Functions

`FatSelectBestWindow`

- Chooses a FAT32 allocation window.
- Prefers the first window with at least 50% free clusters.
- Otherwise prefers the first completely empty window.
- Otherwise selects the window with the greatest free count.

`FatSetupAllocationSupport`

- Computes root directory LBO/size, file area LBO, number of clusters, FAT entry width, and sector/cluster log sizes.
- Caps `NumberOfClusters` to the number describable by the FAT, handling malformed DOS-format volumes and FAT32 too.
- Initializes the virtual volume file cache map for the reserved area and FAT.
- Allocates FAT windows, scans FAT entries, initializes the current free-space bitmap, and sets `ClusterHint`.
- For large FAT32 volumes, first scans all windows for free counts, then selects and materializes one current bitmap window.

`FatTearDownAllocationSupport`

- Frees the windows array and free-cluster bitmap buffer.
- Clears `DirtyFatMcb`.

`FatLookupFileAllocation`

- Looks up a VBO in the file's MCB first.
- If missing, walks the FAT chain from the last known MCB run or the file's first cluster.
- Adds contiguous runs to the MCB while scanning.
- Detects corrupt chains: available/reserved/bad entries inside a file chain, VBO wraparound, or chain length beyond volume size.
- Handles `MAXULONG - 1` lookup sentinel used by `FatLookupFileAllocationSize`.
- Reports `EndOnMax` for the maximal FAT file case.

`FatAddFileAllocation`

- Ensures real allocation size is known before extending.
- For first allocation, obtains the dirent, allocates disk space into the file MCB, updates `FirstClusterOfFile` and the dirent low/high first-cluster fields.
- For extension, allocates into a temporary MCB using the last allocated cluster as a hint, grows cache-manager file sizes, then merges the new allocation into the file MCB.
- Has detailed unwind paths for cache-size growth failure, dirent update failure, MCB failure, and FAT update failure.

`FatTruncateFileAllocation`

- Rounds requested size to a cluster boundary unless truncating to zero.
- No-ops when requested allocation is already satisfied.
- For truncation to zero, updates the dirent first-cluster fields to zero before deallocating clusters.
- For partial truncation, splits the existing MCB at the target VBO and deallocates the remainder.
- Notes deliberate leak-tolerant behavior in some failure cases: consistent in-memory/on-disk metadata is preferred over risky reallocation.

`FatLookupFileAllocationSize`

- Calls `FatLookupFileAllocation` with sentinel `MAXULONG - 1`.
- Fills in the true allocation size after FAT chain traversal.
- Raises corruption if recorded file size exceeds discovered allocation size.

`FatAllocateDiskSpace`

- Rounds requested bytes to clusters and handles the 4 GiB minus 1 maximal allocation case.
- Reserves global free-cluster count under `ChangeBitMapResource` and the bitmap mutex before searching.
- Honors an absolute cluster hint when possible, including FAT32 window switches.
- Supports exact-match allocation for callers such as defrag/move operations.
- Allocates either one contiguous run or multiple fragmented runs, chaining them in the FAT and describing them in the output MCB.
- On failures, unwinds bitmap reservations, free-cluster counts, MCB runs, and FAT allocations.

`FatDeallocateDiskSpace`

- Optionally zeroes the disk allocation before freeing, using MDL-backed synchronous write-through IRPs capped at `MAX_ZERO_MDL_SIZE`.
- Writes `FAT_CLUSTER_AVAILABLE` into each FAT run first.
- Only after FAT updates succeed does it clear bitmap bits and update per-window/global free counts.
- Handles deallocations spanning FAT32 windows.
- On abnormal termination before bitmap/free-count updates, attempts to reconstruct FAT chains from the MCB.

`FatSplitAllocation`

- Moves all MCB runs from `SplitAtVbo` onward into `RemainingMcb`, rebasing them to VBO zero.
- Writes `FAT_CLUSTER_LAST` into the last cluster of the retained chain.
- On failure, moves runs back into the original MCB.

`FatMergeAllocation`

- Appends zero-based runs from `SecondMcb` to the end of `Mcb`.
- Links the old last cluster to the first cluster of `SecondMcb`.
- On failure, removes appended MCB runs from the first MCB.

`FatInterpretClusterType`

- Normalizes FAT12/FAT16/FAT32 entries and classifies them as available, next, reserved, bad, or last.
- Masks FAT32 entries with `FAT32_ENTRY_MASK`.

`FatLookupFatEntry`

- Reads one FAT entry using cache-manager mappings.
- FAT12 pins the whole FAT because 12-bit entries can cross page boundaries.
- FAT16/FAT32 pin and reuse one page through `FAT_ENUMERATION_CONTEXT`.
- Validates indices before reading.

`FatSetFatEntry`

- Writes one FAT entry.
- Special-cases `FAT_DIRTY_BIT_INDEX` to set FAT clean/dirty volume state and temporarily disables normal dirty-volume semantics.
- Updates `DirtyFatMcb` for affected sectors.
- Preserves FAT32 reserved high bits for normal file-heap entries.
- Uses write-through unpinning for clean-volume updates or mount-in-progress corruption-sensitive writes.

`FatSetFatRun`

- Bulk-writes a contiguous cluster range as either a chained allocation or free entries.
- FAT12 pins the whole FAT and updates 12-bit entries under the free-cluster bitmap mutex.
- FAT16 pins all needed pages for the range.
- FAT32 processes chunks capped by `MAXCOUNTCLUS` to avoid pinning huge FAT spans.
- FAT32 unwind walks backward and restores changed entries when a later chunk fails.

`FatLogOf`

- Computes log2 for powers of two.
- Bugchecks if given a non-power-of-two value.

`FatExamineFatEntries`

- Scans FAT entries to initialize or refresh free-space data.
- Modes:
  - setup FAT32 windows and total free count,
  - switch the current bitmap window,
  - fill caller-provided bitmap for arbitrary FAT32 volume bitmap queries.
- Reads FAT12 whole, FAT16/FAT32 page by page, optionally prefetching pages on newer NTDDI.
- Tracks free/allocated runs, sets or clears bitmap bits, updates window free counts, tracks total free clusters when requested, and populates bad-block MCB entries.
- Swaps in a newly built bitmap only after a successful scan.

## Synchronization Model

- Free-cluster bitmap access is protected by `FreeClusterBitMapMutex`.
- Allocation/deallocation also uses `ChangeBitMapResource`, shared for normal bitmap/free-count changes and exclusive for FAT32 window switches.
- Many public allocation routines require the global critical region and are annotated with `_Requires_lock_held_(_Global_critical_region_)`.
- `FatSetFatEntry` and `FatSetFatRun` contain architecture-specific locking for non-atomic narrow writes on ALPHA.
- FAT32 current-window changes are designed to be atomic from the perspective of allocation state: build a temporary bitmap, then swap it into `Vcb`.

## Error Handling and Recovery

- The file relies heavily on SEH-style `try/finally` unwind blocks.
- Allocation paths reserve free counts before writing FAT entries and carefully restore them on failure.
- Deallocation writes FAT entries before clearing bitmap bits so clusters are not reused until disk state says they are free.
- Some truncate failure cases intentionally tolerate leaked clusters to avoid making metadata less consistent.
- Corrupt FAT chains raise `STATUS_FILE_CORRUPT_ERROR` and call `FatPopUpFileCorrupt`.

## Important Edge Cases

- FAT12 12-bit entries can straddle bytes/sectors/pages.
- FAT32 entries preserve reserved high bits.
- A file allocation size may be initially unknown and represented by `FCB_LOOKUP_ALLOCATIONSIZE_HINT`.
- Maximal FAT file size can wrap 32-bit byte counts; several paths special-case `0xFFFFFFFF` and VBO wrap.
- FAT32 large volumes may require switching allocation windows before satisfying a hint.
- Exact-match requests can fail without raising when contiguous placement is impossible.

## ReactOS-Specific Notes

- `FatSelectBestWindow` is marked `static` under `__REACTOS__`.
- Some FAT32 scan pointer arithmetic differs under `__REACTOS__` because `FatBuffer` is a `PUSHORT` while reading 32-bit entries.
- The file is largely derived from Microsoft FastFAT style code, with ReactOS compatibility conditionals.
