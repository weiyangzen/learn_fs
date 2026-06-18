# File Research: sources/windows/reactos/drivers/filesystems/udfs/fastio.cpp

`fastio.cpp` implements UDFS fast I/O and Cache Manager/Memory Manager callback plumbing. It is not a normal read/write implementation; most routines either answer fast-I/O eligibility questions, serve cached metadata queries, or acquire/release FCB resources around section creation, lazy write, read-ahead, modified page writer, and `CcFlush`.

Key entry points:
- `UDFFastIoCheckIfPossible()` rejects volume and directory objects, then delegates byte-range lock checks to `FsRtlFastCheckLockForRead()` or `FsRtlFastCheckLockForWrite()`.
- `UDFIsFastIoPossible()` returns `FastIoIsNotPossible` if the volume is not mounted, `FastIoIsQuestionable` if file locks exist, otherwise `FastIoIsPossible`.
- `UDFFastIoQueryBasicInfo()`, `UDFFastIoQueryStdInfo()`, and `UDFFastIoQueryNetInfo()` call the corresponding `UDFGet*Information()` helpers from `fileinfo.cpp`; basic and network queries acquire `MainResource` shared unless this is a page file.
- `UDFFastIoAcqCreateSec()` and `UDFFastIoRelCreateSec()` acquire/release both `MainResource` and `PagingIoResource` exclusively and maintain `AcqSectionCount`.
- `UDFAcqLazyWrite()`/`UDFRelLazyWrite()` synchronize lazy writer activity on `PagingIoResource`, set `LazyWriterThreadID`, and temporarily set `FSRTL_CACHE_TOP_LEVEL_IRP`.
- `UDFAcqReadAhead()`/`UDFRelReadAhead()` acquire/release `MainResource` shared for Cache Manager read-ahead.
- `UDFFastIoAcqModWrite()`/`UDFFastIoRelModWrite()` gate modified-page writer operations with `PagingIoResource` and `AcqFlushCount`.
- `UDFFastIoAcqCcFlush()`/`UDFFastIoRelCcFlush()` acquire/release `PagingIoResource` exclusively around `CcFlush`.
- `UDFFastIoCopyWrite()` applies verify-queue backpressure and a 16 MiB-aligned cache-section heuristic before falling through to `FsRtlCopyWrite()`.

Notable behavior and dependencies:
- The file relies heavily on `UDFNTRequiredFCB` resources and state counters: `MainResource`, `PagingIoResource`, `AcqSectionCount`, `AcqFlushCount`, and `LazyWriterThreadID`.
- MDL fast I/O routines are present only as commented stubs, so MDL read/write fast paths are effectively unsupported here.
- Query fast paths use SEH wrappers and set `IoStatus` in finalizers, mirroring the IRP paths but with reduced dispatch overhead.
- Fast I/O is intentionally conservative for directories, volume objects, unmounted volumes, file locks, verify-cache pressure, and certain large cached writes.
