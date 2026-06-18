# sources/distributed-fs/xrootd/src/XrdOss/XrdOssCache.hh

## Purpose
Declares the cache-space data model used by the OSS implementation: per-filesystem statistics, logical cache groups, partition allocation vectors, allocation requests, and the static `XrdOssCache` service API.

## Important APIs, types, and functions
Platform macros normalize `statfs/statvfs` as `STATFS_t`, `FS_Stat`, `FS_BLKSZ`, and `FS_FFREE`. `XrdOssCache_Space` is a value object returned to virtual-space callers, holding total/free/max/largest/inode/usage/quota counters. `XrdOssCache_FSData` models one physical filesystem and carries flags `OFFLINE`, `ADJUSTED`, and `REFRESH`. `XrdOssCache_FS` models one configured allocation root and exposes `Add()`, `freeSpace()`, and `getSpace()`. `XrdOssCache_FSAP` links a partition to all allocation paths inside that partition. `XrdOssCache_Group` stores logical group metadata, usage/quota, current round-robin pointer, and static public-group references. `XrdOssCache::allocInfo` is the mutable request/response record used by create and relocate operations.

## Control flow
The header establishes a static-service pattern: configuration creates `XrdOssCache_FS` instances, then runtime operations call `XrdOssCache::Alloc()`, `Adjust()`, and `Find()` without owning a cache object. The public API separates initialization (`Init()` overloads), reporting (`List()`, `DevInfo()`), allocation (`Alloc()`), and scanning (`Scan()`).

## State and persistence
Static members declared here define all cache process state: global mutex, aggregate size/free counters, first/last filesystem list pointers, raw filesystem data list, allocation policy, and booleans indicating quota/usage support. Persistent storage is not in the header but is represented by `Usage`/`Quotas` flags that cause calls into `XrdOssSpace`.

## Dependencies and integration points
Includes `XrdOssVS.hh` for virtual-space partition reporting, `XrdSysError` for display/logging, and `XrdSysPthread` for the cache mutex. Its public fields are intentionally accessible to other OSS files, notably create/relocate/rename code that needs group names, suffixes, and target FS pointers.

## Risks and test signals
The API exposes raw pointers and mutable public fields, so lifetime and locking discipline are implicit. Tests should exercise all platform stat macro variants where supported, `allocInfo` buffer limits, group quota/usage visibility, and callers that use `cgPsfx` to distinguish XA from non-XA cache targets.
