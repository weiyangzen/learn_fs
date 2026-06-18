# File Research: sources/windows/reactos/drivers/filesystems/cdfs/read.c

Implements the common CDFS read path for user files, stream files, and volume/DASD handles.

Key entry points:
- `CdCommonRead()` validates the open type, verifies the FCB/VCB state, checks oplocks and byte-range locks for user files, handles EOF truncation, and performs cached or noncached reads.

Core mechanics:
- Zero-length reads complete successfully immediately.
- Directories and unopened file objects reject reads with `STATUS_INVALID_DEVICE_REQUEST`.
- Volume reads are forced noncached.
- Paging I/O acquires the file shared with starve-exclusive behavior to reduce deadlock risk.
- Noncached reads allocate or reuse a `CD_IO_CONTEXT`, align byte counts to block boundaries, and dispatch to `CdNonCachedRead()` or `CdNonCachedXARead()` for raw-sector/XA files.
- Cached reads initialize the private cache map on first use, set 64 KiB read-ahead, then use `CcCopyRead()` or `CcMdlRead()`.
- Synchronous non-paging reads advance `CurrentByteOffset`.

Important invariants:
- Unaligned noncached reads require a waitable path; otherwise the request is posted.
- Reads past EOF return `STATUS_END_OF_FILE`; reads crossing EOF are truncated unless extended DASD I/O is allowed.
- If aligned noncached I/O reads extra bytes beyond logical EOF/truncated length, the extra user-buffer range is zeroed under SEH.
- Pending noncached I/O retains the file resource through the asynchronous I/O context.

Filesystem relevance:
- This is the primary data path for file reads, directory stream reads, metadata stream reads, and raw volume reads.
- It integrates CDFS file verification, cache manager use, oplock package callbacks, file locks, and XA-sector reads.

Notable risks:
- Noncached raw/XA reads are sensitive to sector alignment, buffer probing, and whether the caller can block.
- User-buffer zeroing is protected, but invalid user buffers still translate into raised `STATUS_INVALID_USER_BUFFER`.
