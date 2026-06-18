# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsi.hh

Purpose: declares the public classes of the checksum-sidecar plugin: directory wrapper, file wrapper, AIO object pool, and top-level OSS handler.

Important APIs/types: `XrdOssCsiDir` wraps `Opendir/Readdir` to hide tag files. `XrdOssCsiFile` overrides normal, vector, async, and page read/write methods plus flush, fsync, fstat, truncate, and verification status. It owns a shared `puMapItem_t` containing refcount, mutex, page manager, data/tag paths, and unlink marker. Static `mapTake/mapRelease` and `pumap_` coordinate all opens by tag path. AIO lifecycle is counted by `aioInc/aioDec/aioWait`. `XrdOssCsi` extends `XrdOssHandler`, adjusts feature flags to add filesystem checksums, page read/write, and no-sendfile, and exposes `tagOpenEnv()`.

State/control: `XrdOssCsiFile` has `rdonly_`, parent OSS pointer, tident, config reference, shared page state, and AIO object store. Close waits for all AIOs before releasing page state. The map refcount is separate from `shared_ptr` lifetime and drives removal from `pumap_`.

Dependencies/integration: depends on XRootD OSS interfaces, scheduler, config, pages, and handler abstractions. Risks include refcount correctness, deadlock around AIO waiters, feature flag accuracy, and raw `const char* tident` lifetime. Tests should stress concurrent opens, close while AIOs run, readonly/write transitions, and map removal after unlink/rename.
