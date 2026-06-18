# File Research: sources/windows/reactos/drivers/filesystems/udfs/flush.cpp

`flush.cpp` implements `IRP_MJ_FLUSH_BUFFERS` plus internal recursive flush helpers for files, directories, stream directories, volume metadata, and the write cache. It coordinates NT Cache Manager flushing with UDF metadata persistence and lower-device flush forwarding.

Primary dispatch flow:
- `UDFFlush()` creates an IRP context, manages top-level IRP state, and delegates to `UDFCommonFlush()`.
- `UDFCommonFlush()` posts non-waitable flushes, distinguishes volume/root flushes from single-file flushes, acquires VCB/FCB resources, and completes or forwards the IRP.
- Volume/root flushes acquire `VCBResource` exclusively and call `UDFFlushLogicalVolume()`.
- Regular file flushes acquire VCB shared and FCB `MainResource` exclusive, then call `UDFFlushAFile()`.

Flush helpers:
- `UDFFlushAFile()` writes security metadata, flushes stream directories, calls `CcFlushCache()` when the cached file is modified or not yet marked flushed, updates modify time/archive state, syncs allocation size in the directory index, and calls `UDFFlushFile__()`.
- `UDFFlushADirectory()` writes directory security, recurses into stream directories, scans directory entries, flushes child directories/files, checks for break requests, and flushes the directory file itself.
- `UDFFlushLogicalVolume()` skips raw, read-only, or unmounted volumes; otherwise it flushes from the root, optionally performs verify writes, unmounts internal UDF structures, flushes `FastCache`, and clears modified state unless this is a lite flush.
- `UDFFlushCompletion()` preserves pending state and converts `STATUS_INVALID_DEVICE_REQUEST` from lower drivers into success.
- `UDFFlushTryBreak()` sets a flush-break request flag; `UDFFlushIsBreaking()` currently returns `FALSE` before checking flags, so break requests are effectively advisory/disabled in this build.

Notable behavior and dependencies:
- The file uses UDF-specific cache APIs such as `WCacheFlushBlocks__()`, `WCacheFlushAll__()`, `UDFVFlush()`, `UDFUmount__()`, `UDFPreClrModified()`, and `UDFClrModified()`.
- Lower-device flush forwarding is conditional on `Vcb->FlushMedia`; otherwise the IRP is completed locally.
- Flush updates are tied to `FO_FILE_MODIFIED`, `FO_FILE_SIZE_CHANGED`, `UDF_CCB_WRITE_TIME_SET`, compatibility flags, and archive-bit policy.
