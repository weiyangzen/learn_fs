# File Research: sources/windows/reactos/drivers/filesystems/cdfs/allocsup.c

## Scope And Purpose

`allocsup.c` implements CDFS allocation mapping through `CD_MCB`. It maps file offsets to logical CD disk offsets, lazily loads allocation extents from directory entries, supports multi-extent and interleaved files, and manages MCB storage lifetime.

Complete file read: 935 lines.

## Main Components

- `CdLookupAllocation` is the main lookup path. It returns the logical disk offset and byte count for a file offset. If the MCB lacks the mapping, it walks the parent directory's dirents, adds all allocation extents for the file, and retries.
- `CdAddAllocationFromDirent` grows the MCB array when needed and adds one extent from a `DIRENT`, converting block offsets and interleave sizes to bytes.
- `CdAddInitialAllocation` initializes the single aligned MCB entry used for directory/path-table style streams.
- `CdTruncateAllocation` truncates the MCB at the entry containing a starting file offset.
- `CdInitializeMcb` initializes an FCB's MCB to use the embedded single entry.
- `CdUninitializeMcb` frees an expanded MCB array.
- `CdFindMcbEntry` linearly finds the entry containing a file offset or the insertion point for a missing entry.
- `CdDiskOffsetFromMcbEntry` converts a file offset within an MCB entry to a disk offset and contiguous byte count, including interleave data/skip handling.

## Integration Points

This file depends on `cdprocs.h`, FCB locking, parent directory acquisition, dirent enumeration helpers, block-size conversion macros, CDFS pool allocation, and CDFS exception raising. It is used by read and stream code that need logical on-disc locations.

## Notes

- DASD I/O bypasses normal MCB lookup and maps file offset directly to disk offset.
- MCBs are not sparse; adding entry `N` makes it the current last entry.
- Interleaved files may return only the current data-block fragment as contiguous.
- Corrupt multi-extent chains raise `STATUS_DISK_CORRUPT_ERROR`.
