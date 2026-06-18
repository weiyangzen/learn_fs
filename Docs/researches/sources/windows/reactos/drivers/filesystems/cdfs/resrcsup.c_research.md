# File Research: sources/windows/reactos/drivers/filesystems/cdfs/resrcsup.c

Provides resource-acquisition wrappers and cache-manager/memory-manager synchronization callbacks for CDFS.

Key entry points:
- `CdAcquireResource()` centralizes exclusive, shared, and shared-starve-exclusive acquisition with wait/nowait behavior driven by the IRP context.
- `CdAcquireForCache()` and `CdReleaseFromCache()` are cache-manager lazy-writer callbacks for acquiring/releasing an FCB resource shared.
- `CdNoopAcquire()` and `CdNoopRelease()` are no-op callbacks for streams that do not need resource synchronization.
- `CdFilterCallbackAcquireForCreateSection()` acquires resources for section creation through the FS filter callback path.
- `CdReleaseForCreateSection()` releases resources acquired for section creation.

Core mechanics:
- `CdAcquireResource()` raises `STATUS_CANT_WAIT` when nonblocking acquisition fails and `IgnoreWait` is not set.
- Cache acquisition sets `IoGetTopLevelIrp()` to `FSRTL_CACHE_TOP_LEVEL_IRP` and release clears it.
- Section synchronization takes the nonpaged FCB resource exclusive and the file resource shared-starve-exclusive.
- For create-section synchronization, CDFS returns `STATUS_FILE_LOCKED_WITH_ONLY_READERS`, reflecting the read-only filesystem.

Important invariants:
- Resource callbacks must maintain lock order compatible with cache manager and memory manager paths.
- Lazy-writer callbacks expect no top-level IRP on entry and restore it on release.
- Section-acquire takes both `FcbResource` and `Resource`; release must drop both.

Filesystem relevance:
- These callbacks are required for safe cached I/O, mapped sections, and synchronization with CDFS read-only file state.

Notable risks:
- Deadlock avoidance relies on shared-starve-exclusive acquisition for create-section paths.
- No-op callbacks must only be used where synchronization is intentionally unnecessary.
