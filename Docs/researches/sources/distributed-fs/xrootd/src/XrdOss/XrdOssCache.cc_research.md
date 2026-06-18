# sources/distributed-fs/xrootd/src/XrdOss/XrdOssCache.cc

## Purpose
Implements the static cache-space allocator and scanner used by the OSS layer when `oss.space`/legacy `oss.cache` configure one or more writable cache partitions. It tracks filesystem devices, cache groups, allocation roots, free-space estimates, quota/usage hooks, and Linux device identifiers.

## Important APIs, types, and functions
`XrdOssCache_FSData::XrdOssCache_FSData()` records one physical filesystem, its size/free bytes from `statfs/statvfs`, the real path, device id, update time, and OSS-local device/partition ids. `XrdOssCache_FS::XrdOssCache_FS()` validates duplicate group/path pairs, creates XA group subdirectories via `XrdOssPath::genPath()`, joins the global circular FS list, and appends allocation paths to the owning `XrdOssCache_Group`. `Add()` adds unnamed filesystems for reporting only. `freeSpace()` and `getSpace()` expose whole-system, per-path, and per-cache-group space summaries. `XrdOssCache::Alloc()` is the main allocator: it parses requested group/path constraints, chooses a partition by available space and fuzz policy, generates a PFN, optionally creates the file, and pessimistically debits free space. `Adjust()` variants reconcile usage/free-space deltas after creates, truncates, relocations, and symlink-backed files. `Find()`, `Parse()`, `List()`, `DevInfo()`, `MapDevs()`, `MapDM()`, and `Scan()` support symlink lookup, `group:path` parsing, effective-config display, device remapping, and periodic statfs refresh.

## Control flow
Configuration builds `XrdOssCache_FS` objects, then calls `Init()` to wire usage/quota persistence and allocation policy. Runtime create/relocate paths fill `allocInfo`, call `Alloc()`, and later call `Adjust()` once a real data size is known. The scan thread loops forever unless invoked with `cscanint <= 0`; each tick locks the cache, refreshes free-space snapshots, conditionally reads quotas, and reloads persisted usage counters.

## State and persistence
Most state is process-global static data: `fsfirst/fslast` circular list, `fsdata`, global free-space counters, allocation policy (`minAlloc`, `ovhAlloc`, `fuzAlloc`), and group list rooted at `XrdOssCache_Group::fsgroups`. `Mutex` protects mutable runtime counters. Persistence is delegated to `XrdOssSpace` when usage or quotas are configured; group usage is assigned a persistent group id and refreshed from the usage file.

## Dependencies and integration points
Depends on platform `statfs/statvfs`, `XrdOssPath` for cache PFN layout, `XrdOssSpace` for quotas and persistent usage, `XrdOssOpaque` for default group names, `XrdOssTrace` for debug logging, and `/proc/partitions` plus `/sys/devices/virtual/block/*/slaves` on Linux for device mapping. Called by `XrdOssCreate.cc`, `XrdOssReloc.cc`, `XrdOssRename.cc`, and config display/stat reporting.

## Risks and test signals
Allocation correctness depends on stale free-space snapshots being corrected by `Scan()` and by `Adjust()` calls after data movement. Symlink and XA suffix parsing must stay consistent with `XrdOssPath`. Tests should cover duplicate spaces, forced group/path allocation, ENOSPC, directory auto-creation, quota file reload, usage file recovery, Linux DM mapping fallback, and races between allocation and scanner refresh.
