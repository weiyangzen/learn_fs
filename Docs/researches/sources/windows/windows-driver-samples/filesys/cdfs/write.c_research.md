# File Research: sources/windows/windows-driver-samples/filesys/cdfs/write.c

## Purpose

Implements CDFS common write handling. Since CDFS is read-only for normal file data, this path only accepts volume/DASD writes through `UserVolumeOpen` and rejects all other open types.

## Key routine

- `CdCommonWrite`: common entry point for `NtWriteFile` handling in CDFS.

## Behavior

`CdCommonWrite` returns success immediately for zero-length writes. It decodes the file object and requires `TypeOfOpen == UserVolumeOpen`; otherwise it completes with `STATUS_INVALID_DEVICE_REQUEST`.

For volume writes, it acquires the FCB shared and verifies the FCB unless the handle is dismounting the volume. Unless extended DASD I/O is allowed, writes starting beyond file size return `STATUS_END_OF_FILE`, and writes extending beyond file size are truncated to the volume file size.

The routine then block-aligns the requested byte count. If the transfer is unaligned by sector offset or aligned size would exceed the original user buffer, it requires a wait-capable context; otherwise it raises `STATUS_CANT_WAIT` so the request can be posted. In the unaligned-buffer case it avoids writing past the caller buffer by reducing `WriteByteCount` back to `ByteCount`.

## I/O context and completion

The routine initializes `IrpContext->IoContext`, using stack storage for synchronous/wait-capable work and allocating a context for asynchronous work. It sets `Irp->IoStatus.Information` to the intended write byte count and marks the file object `FO_FILE_MODIFIED`.

The actual I/O is delegated to `CdVolumeDasdWrite`. If it returns `STATUS_PENDING`, the IRP is left incomplete and the file resource is not released by this function. Otherwise, errors are normalized through `FsRtlNormalizeNtstatus`, user-induced errors are raised, and partial alignment padding in the caller buffer is zeroed with the local `SafeZeroMemory` wrapper. Synchronous file position is advanced to the computed byte range on success.

## Dependencies

Uses CDFS helpers from `CdProcs.h`: `CdDecodeFileObject`, `CdAcquireFileShared`, `CdReleaseFile`, `CdVerifyFcbOperation`, `CdVolumeDasdWrite`, `CdMapUserBuffer`, `CdFsdPostRequest`, `CdCompleteRequest`, and status raising helpers. It relies on Windows IRP stack write parameters, file object flags, and exception handling.

## Edge cases and notes

- The only supported write surface is a volume open, not a user file open.
- `SafeZeroMemory` catches faults while zeroing user-buffer tail bytes and raises `STATUS_INVALID_USER_BUFFER`.
- `STATUS_CANT_WAIT` is converted into posting through `CdFsdPostRequest`.
- `ReleaseFile` is cleared when lower-level DASD write returns pending, transferring completion/resource responsibility to asynchronous I/O completion.
