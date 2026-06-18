# File Research: sources/windows/windows-driver-samples/filesys/cdfs/resrcsup.c

## Purpose

Centralizes resource acquisition helpers and cache-manager / memory-manager synchronization callbacks.

## Main Entry Points

- `CdAcquireResource`
- `CdAcquireForCache`
- `CdReleaseFromCache`
- `CdNoopAcquire`
- `CdNoopRelease`
- `CdFilterCallbackAcquireForCreateSection`
- `CdReleaseForCreateSection`

## Key Behavior

`CdAcquireResource` wraps `ERESOURCE` acquisition for exclusive, shared, and shared-starve-exclusive modes. It decides whether to wait from `IRP_CONTEXT_FLAG_WAIT` unless `IgnoreWait` is set. If it cannot acquire and waiting was required, it raises `STATUS_CANT_WAIT`.

`CdAcquireForCache` and `CdReleaseFromCache` are cache-manager lazy-writer callbacks. The acquire path takes the FCB resource shared and sets top-level IRP to `FSRTL_CACHE_TOP_LEVEL_IRP`; release clears the top-level IRP and releases the resource.

`CdNoopAcquire` and `CdNoopRelease` are no-op callbacks for cases where synchronization is intentionally unnecessary.

`CdFilterCallbackAcquireForCreateSection` handles section synchronization. It acquires the nonpaged FCB resource exclusively, then takes the main file resource shared with starve-exclusive behavior to avoid create-section/read-cache deadlocks. Because CDFS is read-only, create-section synchronization reports `STATUS_FILE_LOCKED_WITH_ONLY_READERS`.

`CdReleaseForCreateSection` releases the resources acquired for section creation.

## Dependencies

Uses kernel `ERESOURCE` APIs, FsRtl cache top-level IRP conventions, FS filter section callbacks, and FCB resource layout from CDFS structures.
