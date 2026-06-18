# File Research: sources/windows/reactos/drivers/filesystems/fastfat/resrcsup.c

This file implements FastFAT resource acquisition helpers and cache-manager/filter synchronization callbacks.

Key responsibilities:
- Acquire VCB and FCB resources in shared or exclusive mode with wait/no-wait semantics.
- Verify operation legality immediately after resource acquisition and release on abnormal unwind.
- Coordinate normal FCB resources with outstanding asynchronous noncached writes.
- Provide cache-manager callbacks for lazy writer, read-ahead, Cc flush, and no-op cache maps.
- Provide the filesystem-filter callback used when memory manager creates or synchronizes sections.

Important functions:
- `FatAcquireExclusiveVcb_Real`: exclusively acquires `Vcb->Resource`, optionally skipping legality checks.
- `FatAcquireSharedVcb`: shared VCB acquisition with legality verification.
- `FatAcquireExclusiveFcb`: exclusive FCB acquisition; waits for outstanding async writes when needed, then retries.
- `FatAcquireSharedFcb`: shared FCB acquisition with similar async-write coordination.
- `FatAcquireSharedFcbWaitForEx`: no-wait shared acquisition that gives exclusive waiters priority for noncached async I/O.
- `FatAcquireFcbForLazyWrite` / `FatReleaseFcbFromLazyWrite`: cache-manager lazy-writer acquire/release.
- `FatAcquireFcbForReadAhead` / `FatReleaseFcbFromReadAhead`: cache-manager read-ahead acquire/release.
- `FatAcquireForCcFlush` / `FatReleaseForCcFlush`: Fast I/O Cc flush preacquire/release callbacks.
- `FatNoOpAcquire` / `FatNoOpRelease`: callbacks for cache maps that do not need real locking.
- `FatFilterCallbackAcquireForCreateSection`: FS filter callback that acquires main exclusively and reports whether writers exist.

Important interactions:
- Uses `ExAcquireResource*Lite`, `ExAcquireSharedWaitForExclusive`, and `ExReleaseResourceLite`.
- Sets `IoSetTopLevelIrp(FSRTL_CACHE_TOP_LEVEL_IRP)` in cache-manager callbacks to prevent recursive verification/hard-error behavior.
- Lazy writer normally acquires paging I/O resource, but uses the main resource for the EA file.
- Cc flush respects FAT lock ordering: main -> BCB -> paging I/O, and deliberately avoids taking main for directory/EA cases where it would invert ordering.
- Section synchronization returns `STATUS_FILE_LOCKED_WITH_ONLY_READERS` or `STATUS_FILE_LOCKED_WITH_WRITERS` for create-section sync.

Notable behavior and risks:
- FCB acquisition can loop while outstanding async writes drain, preventing conflicting cached/noncached operations from racing.
- Cache-manager callbacks assume they are called in safe system/APC-disabled contexts.
- `FatFilterCallbackAcquireForCreateSection` relies on the default FSRTL release path; changing acquired resources would require a paired custom release.
