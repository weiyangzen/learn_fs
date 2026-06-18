# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/fileinfo_cache.h

This header declares the opaque fileinfo cache used by the SaunaFS FSAL. It provides a C ABI around cached `sau_fileinfo_t` pointers without exposing list/tree internals to DS or export code.

The main public types are `fileinfo_t` as an alias for `sau_fileinfo_t`, opaque `FileInfoCache_t`, and opaque `FileInfoEntry_t`. The lifecycle functions are `createFileInfoCache`, `resetFileInfoCacheParameters`, and `destroyFileInfoCache`. Entry management functions are `acquireFileInfoCache`, `releaseFileInfoCache`, `eraseFileInfoCache`, `popExpiredFileInfoCache`, and `fileInfoEntryFree`. Accessors `extractFileInfo` and `attachFileInfo` move the underlying SaunaFS fileinfo pointer in or out of an acquired entry.

State semantics are part of the contract: acquiring can return an entry whose fileinfo is NULL, meaning the caller must open the file and attach the fileinfo before release; erase is used when opening failed and the entry should not enter the LRU; pop-expired removes an unused entry and transfers responsibility to the caller to release the contained fileinfo and free the entry.

Dependencies are limited to the SaunaFS C API and C++ compatibility guards. Integration points are `ds.c` for pNFS DS I/O reuse and `export.c`/`main.c` for cache creation and destruction.

Risks include caller-owned cleanup requirements that are easy to violate, no explicit error object for full-cache conditions despite comments mentioning NULL, and opaque entries that hide whether fileinfo is attached unless callers use `extractFileInfo`. Test signals should validate lifecycle pairing, failed-open erase, export shutdown draining, and C/C++ include compatibility.
