# File Research: sources/windows/windows-driver-samples/filesys/cdfs/read.c

## Purpose

Implements common CDFS read handling for cached, noncached, paging, MDL, user-file, stream-file, and volume reads.

## Main Entry Point

- `CdCommonRead`

## Key Behavior

Zero-length reads complete immediately with success. Reads are rejected for unopened file objects and directory handles. Volume DASD reads are forced noncached.

The routine extracts waitability, paging I/O, noncached I/O, synchronous I/O, starting offset, and byte count. Paging I/O acquires the file shared with starvation of exclusive waiters; other reads acquire shared normally.

For user-file reads, it checks oplocks through `FsRtlCheckOplock` and verifies byte-range locks with `FsRtlCheckLockForReadAccess` for non-paging I/O.

EOF handling returns `STATUS_END_OF_FILE` when starting beyond EOF and truncates reads that extend past EOF, except for extended DASD volume opens.

## Noncached Reads

Noncached reads align to block boundaries. If an unaligned request needs waiting and the caller cannot wait, it raises `STATUS_CANT_WAIT`. It initializes `CD_IO_CONTEXT` either on the stack or from allocated storage, then calls `CdNonCachedXARead` for raw-sector/XA files or `CdNonCachedRead` otherwise.

On completion it normalizes unexpected I/O errors, raises user-induced errors, zero-fills any padding region when an aligned read returned more than logical bytes, and updates the synchronous file position on success.

## Cached Reads

Cached reads initialize the private cache map with `CcInitializeCacheMap` and a 64 KiB read-ahead granularity. Normal cached reads map the user buffer and call `CcCopyRead`; MDL reads call `CcMdlRead`. Successful synchronous non-paging reads advance `CurrentByteOffset`.

`STATUS_CANT_WAIT` posts the request to the FSP; other statuses complete the IRP directly.

## Dependencies

Uses CDFS FCB verification, oplock helpers, file-lock package, cache-manager callbacks, user-buffer mapping, noncached I/O helpers, XA/raw-sector flags, and CDFS request posting/completion helpers.
