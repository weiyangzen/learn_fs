# File Research: sources/windows/reactos/drivers/filesystems/ntfs/rw.c

## Purpose

`rw.c` implements NTFS read and write IRP handling. It maps file objects to FCBs, locates the requested `$DATA` stream, performs attribute reads/writes through `mft.c`, manages sector alignment for reads, grows streams for user writes when allowed, and serializes writes through FCB or volume resources.

## Read Path

`NtfsReadFile`

- Rejects zero-length reads as success.
- Rejects compressed and encrypted files with `STATUS_NOT_IMPLEMENTED`.
- Reads the file's MFT record.
- Finds the requested data stream by `Fcb->Stream`.
- Reports available data streams to debug output if lookup fails.
- Rejects offsets at or beyond end of stream with `STATUS_END_OF_FILE`.
- Clips reads that extend past stream end and zero-fills the caller's trailing buffer.
- Uses a temporary aligned buffer for unaligned sector reads.
- Reads data through `ReadAttribute`.

`NtfsRead`

- Extracts IRP stack, file object, read length, byte offset, and user buffer.
- Calls `NtfsReadFile`.
- Updates synchronous file-object current byte offset and `IoStatus.Information` on success.

## Write Path

`NtfsWriteFile`

- Rejects zero-length writes with a null buffer as success and non-null buffer as invalid.
- Rejects compressed files.
- Reads the target file record and finds the requested data stream.
- If the write extends the stream:
  - Allows growth only for normal, non-volume, non-paging writes.
  - Calls `SetAttributeDataLength`.
  - Gets updated allocation size.
  - Uses the file's best filename attribute to update the parent directory index entry size via `UpdateFileNameRecord`.
- Rejects disallowed extension attempts with `STATUS_ACCESS_DENIED`.
- Writes through `WriteAttribute`.
- Treats short successful writes as `STATUS_UNEXPECTED_IO_ERROR`.

`NtfsWrite`

- Rejects writes to the main filesystem device object.
- Resolves `FILE_WRITE_TO_END_OF_FILE`.
- Rejects non-volume writes whose byte offset uses the high 32 bits.
- Enforces sector alignment for paging, noncached, volume, and no-intermediate-buffering writes.
- Rejects zero-length writes with no user/MDL buffer as success, otherwise invalid.
- Acquires the volume directory resource for volume writes, paging resource for paging I/O, or FCB main resource for ordinary writes.
- Rejects asynchronous file writes as not implemented.
- Gets and locks the user buffer.
- Calls `NtfsWriteFile`.
- Updates synchronous current byte offset, priority boost, and `IoStatus.Information`.

## Integration

- Uses `ReadFileRecord`, `FindAttribute`, `ReadAttribute`, `WriteAttribute`, `SetAttributeDataLength`, and `UpdateFileNameRecord` from `mft.c`.
- Uses `AttributeDataLength` and `AttributeAllocatedLength` to compute stream bounds and allocation.
- Uses FCB state and compression/encryption predicates from `fcb.c`.
- Uses buffer helpers from `misc.c`.
- Relies on `ntfs.h` contracts for IRP context, FCB, and VCB structures.

## Notable Behavior and Risks

- Compressed and encrypted files are not supported.
- Large file writes are rejected when the high 32 bits of the byte offset are nonzero.
- Async writes are not supported.
- Cached writes, file locks, page-file writes, transactions, and timestamp updates are marked TODO or absent.
- The stream-extension path updates only the best filename/hardlink, with a TODO to update every filename attribute and hardlink.
- In the failure path after `FindAttribute` fails, the code calls `ReleaseAttributeContext(DataContext)` even though `DataContext` may not have been initialized by a failed lookup.
- Read failure handling treats a zero-byte `ReadAttribute` result as failure but returns the existing `Status`, which is still initialized to success in that branch.
