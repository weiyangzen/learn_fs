# File Research: sources/windows/reactos/drivers/filesystems/ntfs/mft.c

## Purpose

`mft.c` is the ReactOS NTFS driver's central metadata and attribute I/O implementation. It reads and writes MFT file records, finds and resizes NTFS attributes, handles data-run backed nonresident attributes, updates directory indexes, allocates new MFT records, updates `$MFTMirr`, and provides file/path lookup helpers over NTFS directory indexes.

## Main Responsibilities

- Create and release `NTFS_ATTR_CONTEXT` objects around copied attribute records.
- Decode and cache nonresident attribute mapping pairs through `LARGE_MCB`.
- Find attributes in a file record, including attribute-list references to extension records.
- Read and write resident and nonresident attributes.
- Resize resident and nonresident attributes, including resident-to-nonresident migration.
- Grow `$MFT` and `$MFT::$BITMAP` when no free file-record slots remain.
- Apply and generate NTFS update-sequence-array fixups for file and index records.
- Add a new MFT record and mark it allocated in `$MFT::$BITMAP`.
- Add a filename entry to a directory's `$I30` index using the B-tree helper layer.
- Search directory indexes and subnodes for exact filename lookup or wildcard enumeration.
- Update parent directory `$FILE_NAME` index-entry sizes after file-size changes.

## Key Functions

`PrepareAttributeContext` and `ReleaseAttributeContext`

- Allocate attribute contexts from `NtfsGlobalData->AttrCtxtLookasideList`.
- Copy the raw `NTFS_ATTR_RECORD` into nonpaged pool.
- For nonresident attributes, initialize run-cache fields and convert mapping pairs into `DataRunsMCB`.
- Release the MCB and copied record on cleanup.

`FindAttribute`

- Iterates attributes with `FindFirstAttribute` / `FindNextAttribute`.
- Matches by type and optional name.
- Returns a prepared context and optional record offset.
- If not found locally, scans the attribute list and recursively reads referenced MFT records.
- Rejects attribute-list references back to the same record as missing/corrupt.

`ReadAttribute`

- For resident attributes, bounds the request to `Resident.ValueLength` and copies from the resident value.
- For nonresident attributes, converts the context MCB back into data runs, walks runs to the requested offset, reads clusters via `NtfsReadDisk`, and zero-fills sparse runs.
- Maintains cache-run fields, but the cache path is disabled with `if (0)`.

`WriteAttribute`

- For resident attributes, finds the matching attribute in the file record, copies into the resident value, updates the file record, and refreshes the caller's context copy.
- For nonresident attributes, converts MCB runs back into mapping pairs, walks target runs, and writes sectors through `NtfsWriteDisk`.
- Does not support writing sparse runs and returns `STATUS_NOT_IMPLEMENTED` for them.

`SetAttributeDataLength`, `SetResidentAttributeDataLength`, and `SetNonResidentAttributeDataLength`

- Check memory-mapped-file truncation with `MmCanFileBeTruncated`.
- Dispatch resizing by resident/nonresident type.
- Grow nonresident attributes by allocating clusters with `NtfsAllocateClusters` and appending runs with `AddRun`.
- Shrink nonresident attributes through `FreeClusters`.
- Resize resident attributes in-record when possible.
- Convert resident attributes to nonresident when they no longer fit, backing up existing data and rewriting it after allocation.
- Update FCB file sizes and cache manager sizes after successful top-level resizing.

`IncreaseMftSize`

- Acquires `Vcb->DirResource` exclusively.
- Creates blank file records and clears their in-use flag.
- Reads `$MFT::$BITMAP`, computes the larger bitmap size, grows `$MFT::$DATA`, optionally grows `$BITMAP`, writes the expanded bitmap, writes blank records, and updates `$MFTMirr`.
- Adds 64 records at a time because `ATTR_RECORD_ALIGNMENT * 8` new bitmap bits are introduced.

`AddNewMftEntry`

- Reads `$MFT::$BITMAP`, masks reserved records `0x10` through `0x17`, finds a free bit starting at 24, marks it used, restores reserved bits, writes the bitmap, and writes the new file record.
- If no free slot exists, calls `IncreaseMftSize` and retries recursively.
- Disables global write support for MFT bitmap sizes beyond 32-bit `RTL_BITMAP` support.

`NtfsAddFilenameToDirectory`

- Reads the parent directory record and its `$I30` `$INDEX_ROOT`.
- Converts the index to a B-tree, inserts the filename key, updates `$INDEX_ALLOCATION`, possibly demotes the root, rebuilds `$INDEX_ROOT`, resizes the resident index-root attribute, writes the parent record, and writes the new index-root payload.
- The comments explicitly describe this as work-in-progress and warn that intermediate failure can leave the directory damaged.

`BrowseIndexEntries`, `BrowseSubNodeIndexEntries`, `NtfsFindMftRecord`, `NtfsLookupFileAt`, and `NtfsFindFileAt`

- Traverse directory `$I30` index roots and optional `$INDEX_ALLOCATION` subnodes.
- Use `$I30` `$BITMAP` to validate subnode allocation.
- Apply fixups to index buffers before scanning.
- Skip DOS-name entries and system entries below `NTFS_FILE_FIRST_USER_FILE`.
- Support exact lookup and wildcard directory enumeration via `CompareFileName`.

`UpdateFileNameRecord` and `UpdateIndexEntryFileNameSize`

- Locate the parent directory's `$I30` index entry for a filename.
- Update `FileName.DataSize` and `FileName.AllocatedSize`.
- Write back either the resident index root or a nonresident index allocation record.

`ReadFileRecord`, `UpdateFileRecord`, `FixupUpdateSequenceArray`, and `AddFixupArray`

- Read/write records through `$MFT::$DATA`.
- Verify and restore update-sequence-array protected sector trailers on read.
- Insert update-sequence numbers before writing and immediately undo them in-memory afterward.

`UpdateMftMirror`

- Reads `$MFTMirr`, locates `$MFTMirr::$DATA` and `$MFT::$DATA`, copies the mirrored prefix of `$MFT`, and writes it into `$MFTMirr::$DATA`.

## Integration

- Uses allocation helpers from `volinfo.c`: `NtfsAllocateClusters`.
- Uses attribute construction/run helpers from `attrib.c`: `AddRun`, `FreeClusters`, `ConvertDataRunsToLargeMCB`, `ConvertLargeMCBToDataRuns`, `DecodeRun`, and filename extraction helpers.
- Uses B-tree helpers from `btree.c` for directory index mutation.
- Uses raw block helpers from `blockdev.c`: `NtfsReadDisk`, `NtfsWriteDisk`, and `NtfsReadSectors`.
- Serves read/write paths in `rw.c`, create paths in `create.c`, directory control in `dirctl.c`, and file information update paths in `finfo.c`.

## Notable Behavior and Risks

- Several write paths are explicitly incomplete: sparse writes, large-file writes through callers, compressed/encrypted streams, robust rollback, and full attribute-list growth are not complete.
- `ReadAttribute` and `WriteAttribute` convert MCBs back to data-run buffers for every nonresident I/O because the run cache is disabled.
- `SetNonResidentAttributeDataLength` forcibly recalculates `HighestVCN` with a FIXME noting sparse files will break this math.
- `NtfsAddFilenameToDirectory` can leave a directory inconsistent if failure occurs after temporarily shrinking `$INDEX_ROOT`.
- Many APIs use `ULONG` offsets/lengths even when NTFS sizes are 64-bit; callers reject or avoid large-file cases in some paths, but this remains a structural limit.
- `FindAttribute` does not guard all malformed attribute lengths itself; it relies heavily on lower-level attribute iterators and assertions.
