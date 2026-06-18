# File Research: sources/windows/reactos/drivers/filesystems/fastfat/easup.c

## Purpose

`easup.c` is the lower-level Extended Attribute support layer for FastFAT. Unlike `ea.c`’s disabled dispatch implementation, this file contains active routines for creating, opening, reading, adding, deleting, pinning, dirtying, and unpinning EA data stored in the hidden FAT file `EA DATA. SF`.

## EA Storage Model

The implementation uses an EA database file in the root directory:

- File name: `EA DATA. SF`
- Attributes: read-only, hidden, system, archive
- Header: `EA_FILE_HEADER`
- Handle indirection:
  - `EaBaseTable[240]`
  - offset tables of 128 `USHORT` entries
- Per-file dirents store an EA handle in `Dirent->ExtendedAttributes`.
- Each handle maps to an `EA_SET_HEADER` plus packed EAs.
- `EA_SECTION_SIZE` is `0x40000`; ranges crossing this boundary are copied through an auxiliary buffer because cache mappings may not be contiguous.

## Query Support Routines

- `FatGetEaLength`
  - Returns zero for FAT32 or zero EA handle.
  - Opens the EA file, reads the EA set, and copies `cbList`.
  - Raises `STATUS_NO_EAS_ON_FILE` if a dirent references missing EA data.
- `FatGetNeedEaCount`
  - Returns zero for zero EA handle.
  - Opens the EA file, reads the EA set, and returns `NeedEaCount`.

## Create/Delete Entry Points

- `FatCreateEa`
  - Builds a packed EA set from a caller-provided full EA list.
  - Validates names and flags.
  - Deduplicates by deleting earlier packed EAs with the same name.
  - Ignores zero-length EA values.
  - Rejects EA payloads larger than `MAXIMUM_EA_SIZE`.
  - Creates/opens the EA file and calls `FatAddEaSet`.
  - Writes `cbList`, copies metadata/payload into the new set, marks dirty, flushes cache, and returns the new handle.
  - Returns handle zero when no EA data remains.
- `FatDeleteEa`
  - Opens the EA file.
  - Raises `STATUS_NO_EAS_ON_FILE` if expected EA data is missing.
  - Calls `FatDeleteEaSet`.
  - Flushes the EA file cache.

## EA File Discovery and Creation

`FatGetEaFile` is the central initializer:

- Acquires `Vcb->EaFcb` shared or exclusive depending on caller need.
- If `Vcb->VirtualEaFile` already exists, verifies the EA FCB and pins the EA dirent.
- Otherwise searches the root directory for `EA DATA. SF`.
- If found:
  - pins the dirent
  - initializes `EaFcb` first cluster, dirent offset, allocation size, file size, and MCB
  - opens the virtual stream file
  - stores it in `Vcb->VirtualEaFile`
- If not found and `CreateFile` is true:
  - allocates disk space for an initial EA header plus offset table
  - creates a root-dir dirent
  - constructs the hidden/system/read-only EA file
  - initializes cache/file sizes
  - writes `EA_FILE_SIGNATURE`
  - initializes base table and offset table entries
  - marks data dirty and flushes
- The routine has unwind paths for allocated disk space, created dirent, stream file references, and locks.

## Reading EA Sets

`FatReadEaSet`:

- Validates handle range: `MIN_EA_HANDLE` through `MAX_EA_HANDLE`.
- Pins the EA file header and the relevant offset table.
- Rejects unused handles.
- Computes the EA set VBO from `EaBaseTable[handle >> 7] + offset`.
- Pins the first cluster of the EA set.
- Verifies `EA_SET_SIGNATURE` and `OwnEaHandle`.
- If the caller wants the whole set and `cbList` spans multiple clusters, repins the full rounded range.

## Deleting EA Sets

`FatDeleteEaSet`:

- Validates handle and maps it through the base/offset tables.
- Pins and verifies the target EA set.
- Computes the cluster count from `cbList`.
- Flushes and purges cache pages around the splice point.
- Splits the target cluster run out of the EA file MCB.
- Merges any tail allocation back around the removed range.
- Shrinks `EaFcb` file/allocation size and updates `EaDirent->FileSize`.
- Updates cache manager file sizes.
- Marks the EA dirent dirty.
- Updates base table and offset table:
  - clears the removed handle to `UNUSED_EA_HANDLE`
  - decrements later offsets/base entries by the removed cluster count
- Deallocates removed disk space.
- Provides detailed abnormal-termination recovery before EA metadata is finalized.

## Adding EA Sets

`FatAddEaSet`:

- Pins the EA header and entire offset table.
- Searches backward for an unused handle, inserting near existing handle clusters when possible.
- Adds a new offset-table cluster if needed.
- Checks max handle and max EA file size constraints.
- Allocates all required disk space atomically.
- Flushes and purges cache at the insertion point.
- Splits and merges MCB ranges to insert:
  - optional new offset-table cluster
  - optional initial EA data
  - new EA set clusters
  - optional tail
- Grows file/allocation size and dirent file size.
- Pins new header, offset table, and EA set.
- Initializes `EA_SET_SIGNATURE` and `OwnEaHandle`.
- Updates base/offset tables, including offsets after insertion.
- Marks modified ranges dirty.
- Returns the new EA handle.
- Has extensive unwind logic to restore MCB layout, file sizes, cache state, and allocated disk space on failure.

## Packed EA Helpers

- `FatAppendPackedEa`
  - Converts a `FILE_FULL_EA_INFORMATION` entry into packed EA form.
  - Reallocates the working EA-set buffer in cluster-sized increments when needed.
  - Increments `NeedEaCount` for `FILE_NEED_EA`.
  - Uppercases EA names in stored packed form.
- `FatDeletePackedEa`
  - Removes one packed EA by offset.
  - Decrements `NeedEaCount` for `EA_NEED_EA_FLAG`.
  - Slides remaining packed data down and zeroes the freed tail.
- `FatLocateNextEa`
  - Computes the next packed EA offset or returns `0xffffffff`.
- `FatLocateEaByName`
  - Case-insensitive search across packed EAs.
- `FatIsEaNameValid`
  - Rejects empty names and names longer than 254 bytes.
  - Allows DBCS lead-byte pairs.
  - Uses FAT ANSI character legality rules without wildcards.

## Cache Pinning Helpers

- `FatPinEaRange`
  - Validates requested range is inside EA file allocation.
  - Pins page-sized chunks with `CcPinRead`.
  - Allocates a larger BCB chain if the fixed array is insufficient.
  - Uses an auxiliary buffer when the requested range crosses an EA section boundary.
- `FatMarkEaRangeDirty`
  - Copies auxiliary data back with `CcCopyWrite` if needed.
  - Marks each pinned BCB dirty with `CcSetDirtyPinnedData`.
- `FatUnpinEaRange`
  - Frees auxiliary buffer.
  - Unpins all BCBs.
  - Frees dynamically allocated BCB chains.

## Notable Risks and Behaviors

- The code is FAT12/FAT16-oriented for EA storage; FAT32 is intentionally excluded in higher-level paths.
- Many routines assume the caller holds the right FCB/VCB locks and is in a waitable context where documented.
- EA file mutation depends on careful cache purge and MCB splicing. The unwind logic is central to crash/failure safety.
- `FileName` parameters in `FatReadEaSet` and `FatDeleteEaSet` are currently marked unused, so owner-name verification described in comments is not enforced here.
