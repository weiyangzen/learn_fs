# File Research: sources/windows/windows-driver-samples/filesys/fastfat/allocsup.c

## Purpose

Implements FastFAT allocation support: FAT scanning, free-cluster bitmap/window setup, file allocation lookup and growth, truncation, cluster allocation/deallocation, MCB split/merge, FAT entry encoding/decoding for FAT12/16/32, and bad-cluster discovery.

## Major data model

The file maintains allocation state in the VCB:

- `AllocationSupport`: root directory offsets/sizes, file-area LBO, number of clusters, FAT entry bit size, log sector/cluster sizes, total free clusters.
- `FreeClusterBitMap`: bitmap for the current allocation window, where set bits represent allocated clusters and clear bits represent free clusters.
- `Windows`: FAT32 window descriptors used when the volume has more clusters than `MAX_CLUSTER_BITMAP_SIZE`.
- `CurrentWindow`: active FAT window whose free bitmap is loaded.
- `ClusterHint`: window-relative allocation hint.
- `DirtyFatMcb`: tracks FAT sectors dirtied by allocation changes.
- `BadBlockMcb`: records bad clusters discovered while scanning.

## Key routines

- `FatSetupAllocationSupport`: computes allocation geometry, initializes/extends the virtual volume file cache, allocates FAT windows, scans FAT entries, chooses an initial window, builds the current free bitmap, and sets the first allocation hint.
- `FatTearDownAllocationSupport`: frees windows and bitmap storage and clears the dirty FAT MCB.
- `FatLookupFileAllocation`: maps a file VBO to LBO using the FCB/DCB MCB, extending the MCB by walking the FAT chain if needed.
- `FatAddFileAllocation`: appends clusters to a file/directory, updates first-cluster dirent fields when allocating an empty file, informs cache manager if needed, and merges new runs.
- `FatTruncateFileAllocation`: trims allocation to a cluster boundary, updates first-cluster fields for truncation to zero, splits allocation, and deallocates removed clusters.
- `FatLookupFileAllocationSize`: forces discovery of true chain allocation size using the special `MAXULONG - 1` lookup path.
- `FatAllocateDiskSpace`: reserves free clusters from the current/free windows, builds an MCB for newly allocated space, writes FAT chains, supports exact-match requests, and handles FAT32 window switching.
- `FatDeallocateDiskSpace`: optionally zeroes data before freeing, marks FAT entries available, clears bitmap bits in the active window, updates window and global free counts, and attempts FAT-chain restoration on failure.
- `FatSplitAllocation` / `FatMergeAllocation`: split and join MCB-described chains by rewriting the terminal or splice FAT entry.
- `FatInterpretClusterType`: classifies FAT entries as available, next, reserved, bad, or last, with FAT12/16 normalization and FAT32 masking.
- `FatLookupFatEntry`: reads a FAT entry using cached/pinned FAT pages, with special handling for FAT12 whole-FAT pinning.
- `FatSetFatEntry`: writes one FAT entry, including the special DOS-style FAT dirty/clean entry path.
- `FatSetFatRun`: writes a contiguous run of FAT entries, linking clusters or freeing them.
- `FatLogOf`: computes log2 for power-of-two values and bugchecks on invalid input.
- `FatExamineFatEntries`: scans FAT ranges to build free bitmaps, initialize FAT32 windows, serve volume bitmap data, and populate bad-cluster state.

## Allocation algorithm

Allocation starts by rounding requested bytes to clusters, with special handling for the maximal 4 GiB minus 1 case. `FatAllocateDiskSpace` first subtracts the requested cluster count from the global free count while holding `ChangeBitMapResource` and `FreeClusterBitMapMutex`, ensuring another thread cannot take the space.

It then searches for a contiguous free run from either an absolute hint or `Vcb->ClusterHint`. If a sufficient run exists and exact-match constraints are met, it reserves bitmap bits, updates window free count, adds the run to the output MCB, and writes the FAT chain.

If no single run satisfies the request, it upgrades to exclusive bitmap-resource access, repeatedly chooses runs from the current or selected FAT32 windows, reserves them, writes FAT entries, links disjoint runs through the prior last cluster, and advances until the requested cluster count is satisfied. FAT32 can switch windows to maintain locality or select a better window by `FatSelectBestWindow`.

## Deallocation and zeroing

`FatDeallocateDiskSpace` first optionally zeroes every run via synchronous write IRPs using zero MDLs capped at `MAX_ZERO_MDL_SIZE` (1 MiB). Zeroing failures are recorded but do not prevent freeing, to avoid leaking volume space.

The actual free operation has two phases: write `FAT_CLUSTER_AVAILABLE` into affected FAT entries, then update in-memory bitmap/window/free counts. This ordering prevents another allocator from taking clusters that would need to be restored if FAT updates fail. On abnormal termination, the routine walks already-processed MCB entries and attempts to rebuild the FAT chain.

## FAT12/16/32 handling

- FAT12 lookup pins the whole FAT because entries can cross byte/page boundaries.
- FAT16 lookup pins one FAT page at a time and reads `USHORT` entries.
- FAT32 lookup pins one FAT page at a time, reads `ULONG` entries, and masks with `FAT32_ENTRY_MASK`.
- FAT32 write paths preserve reserved high bits for normal entries and chunk large `FatSetFatRun` operations with unwind logic because pinning all touched FAT pages may be impractical.

## Failure and unwind behavior

This file is heavily exception-oriented. Growth, truncation, split, merge, allocation, deallocation, and FAT write routines use `try/finally` blocks to reverse partial state:

- `FatAddFileAllocation` rolls back allocation size, cache-manager size changes, first-cluster dirent updates, and newly allocated disk space.
- `FatTruncateFileAllocation` restores in-memory allocation fields when possible, but comments acknowledge cluster leaks may remain after some deallocation failures.
- `FatSplitAllocation` merges MCB runs back on failure.
- `FatMergeAllocation` removes appended MCB runs on failure.
- `FatSetFatRun` has FAT32-specific unwind to restore previously changed entries.

## Dependencies

Depends on FastFAT types/helpers in `FatProcs.h`, cache helpers from `cachesup.c`, MCB wrappers (`FatAddMcbEntry`, `FatLookupMcbEntry`, `FatRemoveMcbEntry`, etc.), FAT geometry macros, Windows cache manager APIs, RTL bitmap APIs, resource/fast mutex synchronization, MDL and IRP I/O APIs, and security/error propagation helpers.

## Edge cases and notes

- FAT32 volumes larger than `MAX_CLUSTER_BITMAP_SIZE` use bucket/window scanning to avoid maintaining a huge bitmap at once.
- `FatExamineFatEntries` handles three distinct roles: setup scan, window switch, and arbitrary bitmap fill.
- `FatLookupFileAllocation` detects corrupt chains that hit available/reserved/bad clusters where a continuation is expected.
- Bad clusters are recorded in `BadBlockMcb` during setup or single-window scans.
- The code contains explicit maximal-file overflow handling where byte counts can wrap to zero or use `0xffffffff`.
