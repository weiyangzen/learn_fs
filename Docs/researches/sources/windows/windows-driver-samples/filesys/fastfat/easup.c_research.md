# File Research: sources/windows/windows-driver-samples/filesys/fastfat/easup.c

This file implements FastFAT extended attribute support backed by the hidden FAT12/FAT16 EA metadata file `EA DATA. SF`. It handles EA length/count lookup, EA set creation/deletion, EA handle table management, packed EA list manipulation, and cache-manager pin/dirty/unpin handling for EA-file ranges.

Key routines:
- `FatGetEaLength` returns the packed EA byte count for a file dirent. It short-circuits to zero on FAT32 or handle zero, then opens the EA file, reads the owning EA set, and copies `cbList`.
- `FatGetNeedEaCount` similarly reads an EA set and returns `NeedEaCount`.
- `FatCreateEa` converts a user `FILE_FULL_EA_INFORMATION` list into FastFAT packed EA records, validates names/flags, removes duplicate names, ignores zero-length values, allocates an EA handle/set, writes the EA-set header/body, and flushes the virtual EA file.
- `FatDeleteEa` opens the EA file and delegates to `FatDeleteEaSet`.
- `FatGetEaFile` lazily locates or creates `EA DATA. SF` in the root directory, initializes `Vcb->EaFcb`, creates the virtual stream file, sets file sizes, allocates initial clusters, initializes `EA_FILE_HEADER`, base table, and offset tables, and unwinds partial creation on failure.
- `FatReadEaSet` validates an EA handle, reads the base/offset table entry, computes the set VBO, pins the EA set, verifies signature/handle ownership, and optionally repins the full set length.
- `FatDeleteEaSet` removes an EA set by purging cache pages, splitting the file allocation around the target cluster range, shrinking the EA file, updating dirent/file sizes, adjusting later base/offset entries, marking metadata dirty, and deallocating removed clusters.
- `FatAddEaSet` allocates and splices clusters for a new EA set, optionally inserts a new offset-table cluster, updates cache/file sizes, initializes the new set header, adjusts base/offset tables, and returns the new EA handle.
- `FatAppendPackedEa`, `FatDeletePackedEa`, `FatLocateNextEa`, and `FatLocateEaByName` implement in-memory packed-EA list editing.
- `FatIsEaNameValid` enforces FAT EA name legality using FAT ANSI character rules and DBCS lead-byte handling.
- `FatPinEaRange`, `FatMarkEaRangeDirty`, and `FatUnpinEaRange` wrap cache-manager pinned access to EA file ranges, including auxiliary buffers when a range crosses an EA section boundary.

Important data model:
- EA data lives in `EA DATA. SF`, not in each normal file.
- A file dirent’s `ExtendedAttributes` field is an EA handle.
- `EA_FILE_HEADER` contains base offsets for EA handle groups.
- Offset-table entries map each handle to a cluster offset, with `UNUSED_EA_HANDLE` marking free handles.
- `EA_SET_HEADER` stores the owning handle, needed-EA count, owner filename, packed list length, and packed EA records.
- The code assumes EA support is meaningful for FAT12/FAT16; FAT32 lookup returns zero EA length.

Concurrency and cache behavior:
- Callers are expected to hold filesystem critical-region state.
- EA FCB access is acquired shared or exclusive depending on mutation.
- Creation/deletion paths require waitable execution and exclusive EA FCB access.
- Cache coherency is explicit: dirty pinned data is marked, caches are flushed, purge retries are used before allocation splicing, and `CcSetFileSizes` updates cache-manager file sizes after growth/shrink.
- Ranges spanning `EA_SECTION_SIZE` or too many pages use auxiliary buffers to avoid assumptions about contiguous mapped system addresses.

Failure and corruption behavior:
- Invalid handles raise `STATUS_NONEXISTENT_EA_ENTRY`.
- Missing required EA file raises `STATUS_NO_EAS_ON_FILE`.
- Bad signatures, wrong owning handle, or impossible lengths raise data/corruption status.
- Oversized EA lists raise `STATUS_EA_TOO_LARGE`.
- Purge failure raises `STATUS_UNABLE_TO_DELETE_SECTION`.
- Most mutating paths maintain unwind state so partially allocated clusters, dirents, Mcbs, stream references, and cache sizes can be restored where possible.

Role in the subset:
- This is a dense example of legacy Windows FAT metadata support layered over a simple on-disk filesystem using a hidden metadata file, cache-manager pins, and FAT-chain splicing.
