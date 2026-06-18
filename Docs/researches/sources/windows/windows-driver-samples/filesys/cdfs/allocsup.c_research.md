# File Research: sources/windows/windows-driver-samples/filesys/cdfs/allocsup.c

## Purpose

`allocsup.c` implements CDFS allocation mapping support around the internal `CD_MCB` structure. It maps logical file offsets to logical on-disc byte offsets and contiguous byte counts, using 2048-byte cooked CD sectors rather than raw 2352-byte XA sectors.

The file handles normal single-extent mappings, multi-extent files represented by multiple dirents, directory/path-table stream biasing, and interleaved extents.

## Main Routines

- `CdLookupAllocation`
  - Main lookup entry point.
  - Returns `DiskOffset` and `ByteCount` for a valid file offset.
  - Special-cases `VolumeDasdFcb` by returning the input `FileOffset` directly.
  - Looks in the FCB MCB first.
  - If the MCB lacks the requested mapping, acquires the parent directory, walks dirents from the file's first dirent offset, lazily loads every extent into the MCB, then retries lookup.
  - Raises `STATUS_DISK_CORRUPT_ERROR` if the second pass still cannot resolve the mapping or a multi-extent chain has no next dirent.

- `CdAddAllocationFromDirent`
  - Adds one dirent extent into an FCB MCB at a requested slot.
  - Doubles the MCB array when the embedded/small array is full.
  - Stores starting disc offset, byte count, file offset, and interleave geometry.
  - Rounds the last extent byte count to a logical block boundary.
  - Converts `FileUnitSize` and `InterleaveGapSize` from logical blocks to bytes.

- `CdAddInitialAllocation`
  - Creates the initial mapping for directory/path-table streams.
  - Biases `DiskOffset` backward by `Fcb->StreamOffset` so cached stream offsets can begin on sector boundaries.
  - Requires an empty MCB and non-data FCB.

- `CdTruncateAllocation`
  - Drops MCB entries starting at the entry containing `StartingFileOffset`.
  - Used when directory stream size or cached allocation needs to be reset.

- `CdInitializeMcb`
  - Initializes an FCB's MCB with a single embedded `Fcb->McbEntry`.

- `CdUninitializeMcb`
  - Frees an allocated MCB array when more than the embedded entry was used.

- `CdFindMcbEntry`
  - Linear search for the MCB entry containing a file offset.
  - Returns the insertion index when no current entry covers the offset.

- `CdDiskOffsetFromMcbEntry`
  - Computes the disc offset and contiguous byte count within a selected MCB entry.
  - Fast path for non-interleaved extents.
  - For interleaved extents, walks file-data blocks while skipping gap blocks on disc.
  - Caps returned byte count at `MAXULONG`.

## Key Data Model

Each `CD_MCB_ENTRY` stores:

- `FileOffset`: logical offset in the file.
- `DiskOffset`: logical cooked disc offset, already biased for XAR and directory stream alignment.
- `ByteCount`: file bytes represented by this extent.
- `DataBlockByteCount`: data bytes in each interleave unit.
- `TotalBlockByteCount`: data plus skipped gap bytes per interleave unit.

The MCB is non-sparse and append-only during loading; adding an extent always advances `CurrentEntryCount`.

## Integration

`allocsup.c` depends on dirent enumeration (`CdLookupDirent`, `CdLookupNextDirent`, `CdUpdateDirentFromRawDirent`), FCB locking (`CdLockFcb`/`CdUnlockFcb`), file acquisition on the parent directory, and block/sector conversion macros from `cdprocs.h`.

It is used by read and cache paths that need to translate logical stream offsets into disc reads.

## Risk Notes

- The MCB search is linear by design; this is acceptable for typical CD files but can scale poorly with many extents.
- Lazy population trusts multi-dirent ordering in the parent directory; malformed chains raise corruption statuses.
- Interleave math is central to correctness. Off-by-one or block-size errors would return wrong physical reads.
- The module assumes callers request valid file ranges; invalid or beyond-file offsets are not independently sanitized here.
