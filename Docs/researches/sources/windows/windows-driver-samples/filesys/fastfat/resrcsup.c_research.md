# File Research: sources/windows/windows-driver-samples/filesys/fastfat/resrcsup.c

## Purpose
Implements FastFAT resource acquisition/release helpers for VCBs, FCBs, cache-manager callbacks, read-ahead, lazy writer, Cc flush, no-op cache callbacks, and section synchronization.

## Main Entry Points
- `FatAcquireExclusiveVcb_Real`
- `FatAcquireSharedVcb`
- `FatAcquireExclusiveFcb`
- `FatAcquireSharedFcb`
- `FatAcquireSharedFcbWaitForEx`
- `FatAcquireFcbForLazyWrite`
- `FatReleaseFcbFromLazyWrite`
- `FatAcquireFcbForReadAhead`
- `FatReleaseFcbFromReadAhead`
- `FatAcquireForCcFlush`
- `FatReleaseForCcFlush`
- `FatNoOpAcquire`
- `FatNoOpRelease`
- `FatFilterCallbackAcquireForCreateSection`

## VCB Acquisition
Exclusive and shared VCB acquisition use `ExAcquireResource*Lite` with wait behavior from `IRP_CONTEXT_FLAG_WAIT`. After acquisition they call `FatVerifyOperationIsLegal` unless explicitly suppressed. If verification raises, the resource is released in the abnormal-termination path.

## FCB Acquisition
Exclusive and shared FCB acquisition retry around outstanding async noncached writes. If `OutstandingAsyncWrites` is nonzero and the current operation should not proceed concurrently, the code waits on `OutstandingAsyncEvent`, releases the FCB, and retries acquisition.

`FatAcquireSharedFcbWaitForEx` is a specialized nonwaitable, noncached path that uses `ExAcquireSharedWaitForExclusive` so exclusive waiters are honored before the shared read proceeds.

## Lazy Writer And Read Ahead
`FatAcquireFcbForLazyWrite` acquires the paging I/O resource for normal files, but the main resource for the EA file. It marks the current thread as the FCB lazy writer thread and sets `IoGetTopLevelIrp` to `FSRTL_CACHE_TOP_LEVEL_IRP` so reentrant cache-manager activity is treated correctly.

`FatReleaseFcbFromLazyWrite` clears the lazy writer marker, releases the matching resource, and clears the top-level IRP sentinel.

`FatAcquireFcbForReadAhead` acquires the main resource shared to synchronize with purges and also sets the cache top-level IRP sentinel. The release routine clears the sentinel and releases the main resource.

## Cc Flush Handling
`FatAcquireForCcFlush` installs the cache top-level IRP sentinel if none exists, decodes the file object, and acquires resources in a way that avoids FAT’s lock-order inversion risk. The file comments explicitly state FAT lock order as main resource, then BCB, then paging I/O resource. Directories and EA files avoid taking main in this path; regular files may take both main and paging.

`FatReleaseForCcFlush` clears the sentinel when appropriate and releases the resources acquired for flush.

## No-op Cache Callbacks
`FatNoOpAcquire` and `FatNoOpRelease` do not acquire a resource. They only set and clear `FSRTL_CACHE_TOP_LEVEL_IRP`, used where cache callbacks require a shape-compatible acquire/release pair but no actual resource synchronization.

## Section Synchronization
`FatFilterCallbackAcquireForCreateSection` handles MM/filter acquire-for-section synchronization. It acquires the FCB main resource exclusive and returns:
- `STATUS_FSFILTER_OP_COMPLETED_SUCCESSFULLY` for non-create-section sync types.
- `STATUS_FILE_LOCKED_WITH_ONLY_READERS` when no writers are present.
- `STATUS_FILE_LOCKED_WITH_WRITERS` when write handles exist.

The comment notes that the default FSRTL release routine is expected because this routine acquires only the main resource.

## Important Notes
This file centralizes many resource ordering rules that other FastFAT paths rely on. The top-level IRP sentinel behavior is as important as the resource operations: it prevents cache-manager and memory-manager reentry from being mistaken for ordinary user filesystem recursion.
