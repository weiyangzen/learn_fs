## sources/distributed-fs/xrootd/src/XrdEc/XrdEcConfig.hh

### Purpose
This header defines the singleton module configuration for XrdEc. It mainly caches `RedundancyProvider` instances keyed by erasure-code layout and controls whether XrdCl plugin support is enabled inside EC-created files/archives.

### Important APIs, Types, and Functions
- `Config::Instance()` returns a process-local singleton.
- `GetRedundancy(const ObjCfg &objcfg)` returns a cached `RedundancyProvider` for `nbchunks`, `nbparity`, and `datasize`.
- `enable_plugins` is a public boolean used when constructing `XrdCl::ZipArchive` or `XrdCl::File`.

### Control Flow
`GetRedundancy` builds a string key from object layout values, locks `mtx`, looks up an existing provider, and constructs one in-place if absent.

### State and Persistence
State is process-local: an unordered map of redundancy providers and a mutex. There is no persistence across processes. The singleton defaults `enable_plugins` to true, while `XrdClEcHandler` can disable it to avoid recursive plugin use.

### Dependencies and Integration Points
The header includes `XrdEcRedundancyProvider.hh` and `XrdEcObjCfg.hh`. Reader recovery and write-buffer encoding paths use `Config::Instance().GetRedundancy`.

### Risks and Edge Cases
The cache key omits `chunksize`, `nbdata`, and digest choice directly; `datasize` plus `nbchunks` and `nbparity` implies `nbdata` and chunk size for valid configurations, but only if object configs are internally consistent. The returned reference remains valid because unordered-map nodes are stable for references across rehash, but lifecycle is singleton-global. Public mutable `enable_plugins` is not synchronized.

### Test Signals
Tests should verify that identical layouts reuse a provider, different layouts create distinct providers, and plugin toggling affects newly created XrdCl archive/file objects without causing recursive EC plugin loading.
