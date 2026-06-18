# File Research: sources/windows/reactos/drivers/filesystems/cdfs/write.c

Implements the limited CDFS write path. CDFS is read-only for files, so writes are only accepted for volume/DASD handles.

Key entry points:
- `CdCommonWrite()` validates a write request, permits only `UserVolumeOpen`, verifies the volume unless dismount-on-close is set, bounds/alignment-adjusts the request, prepares a `CD_IO_CONTEXT`, marks the file object modified, and dispatches to `CdVolumeDasdWrite()`.

Core mechanics:
- Zero-length writes complete successfully.
- Non-volume writes fail with `STATUS_INVALID_DEVICE_REQUEST`.
- Writes beyond EOF return `STATUS_END_OF_FILE`; writes crossing EOF are truncated unless extended DASD I/O is allowed.
- Byte counts are block-aligned, but unaligned writes require a waitable path; otherwise the request is posted with `STATUS_CANT_WAIT`.
- Pending noncached writes hold the file resource through the async I/O context.
- Successful synchronous writes update `CurrentByteOffset`.
- If alignment caused extra bytes to be touched, the extra user-buffer range is zeroed and reported bytes are reduced to the logical byte count.

Important invariants:
- CDFS does not write regular file data; all writes are raw volume writes.
- `FO_FILE_MODIFIED` is set conservatively so close will trigger verification.
- User-induced errors are raised for normal hard-error handling; other failures are normalized to unexpected I/O error.

Filesystem relevance:
- Supports raw DASD access scenarios such as volume-management or dismount workflows while preserving normal read-only filesystem semantics.

Notable risks:
- The write path shares noncached alignment/posting patterns with read, so buffer validity and sector alignment are critical.
- Raw volume writes can invalidate assumptions about mounted media; the code intentionally marks the handle modified to force later verify behavior.
