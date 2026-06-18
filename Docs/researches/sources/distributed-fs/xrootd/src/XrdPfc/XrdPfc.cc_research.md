<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfc.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfc.cc

## Purpose

`XrdPfc.cc` implements the main proxy file cache plugin entry point and the runtime `XrdPfc::Cache` object. It decides whether to wrap remote IO, manages active cached files, write-back queues, RAM buffers, prefetch scheduling, cache metadata/xattrs, local-file-path lookup, deferred opens, stat/only-if-cached behavior, unlink/eviction, and HTTP cache-control validation.

## Important APIs, Types, And Functions

- `XrdOucGetCache()` is the exported plugin factory. It obtains or creates a scheduler, creates/configures the singleton cache, starts resource monitor/write/prefetch threads, registers `XrdPfcFSctl`, and returns `XrdOucCache*`.
- Singleton APIs: `CreateInstance()`, `GetInstance()`, `TheOne()`, `Conf()`, and `ResMon()`.
- IO APIs: `Attach()`, `Prepare()`, `Stat()`, `LocalFilePath()`, `ConsiderCached()`, and `Unlink()`.
- Active-file APIs: `GetFile()`, `ReleaseFile()`, `inc_ref_cnt()`, `dec_ref_cnt()`, `schedule_file_sync()`, and `FileSyncDone()`.
- Write queue APIs: `AddWriteTask()`, `RemoveWriteQEntriesFor()`, `ProcessWriteTasks()`, and `WritesSinceLastCall()`.
- RAM APIs: `RequestRAM()` and `ReleaseRAM()` maintain an allocation budget and reusable standard-size block list.
- Prefetch APIs: `RegisterPrefetchFile()`, `DeRegisterPrefetchFile()`, `GetNextFileToPrefetch()`, and `Prefetch()`.
- Metadata APIs: `WriteCacheControlXAttr()`, `WriteFileSizeXAttr()`, `DetermineFullFileSize()`, `GetCacheControlXAttr()`, `DecideIfConsideredCached()`, and `is_http_cache_valid()`.

## Control Flow

Startup enters through `XrdOucGetCache()`: config is parsed before background threads are launched. `Attach()` passes through writes unless write-through is enabled, asks configured decision plugins whether the logical filename should be cached, and wraps eligible reads in `IOFile` or block-mode IO. If a local file cannot be opened, it falls back to the original remote IO.

Read paths use `GetFile()` to serialize creation of one `File` per local path. The active map stores `nullptr` while an open is in progress so other attachers wait. Refcount drops go through `dec_ref_cnt()`; the last reference may schedule a final sync, close the file, remove it from `m_active`, emit a g-stream `file_close` JSON record, and delete the `File`.

`Prepare()` implements deferred open by returning `1` when a `.cinfo` metadata file exists. It also intercepts `/xrdpfc_command/` URLs by scheduling a command job and returning `-EAGAIN`. `LocalFilePath()`, `Stat()`, and `ConsiderCached()` read active `File` state or on-disk `.cinfo` metadata to determine completeness and only-if-cached status. `UnlinkFile()` coordinates active-file emergency shutdown or protected placeholder insertion, removes queued blocks, unlinks data plus `.cinfo`, updates resource monitor purge accounting, and broadcasts active-map changes.

## State And Persistence

Runtime state includes the singleton pointer, scheduler pointer, config, OSS handle, trace/log objects, decision plugins, purge plugin, resource monitor, active file map, purge-delay set, write queue, RAM block pool, and prefetch list. Persistent state is the cache data file, `.cinfo` metadata file, xattrs `pfc.cache-control` and `pfc.fsize`, chmod changes for direct local access, and resource-monitor accounting.

## Dependencies And Integration Points

The file integrates with `XrdOucCache`, `XrdOucCacheIO`, `XrdOucEnv`, `XrdOss`, `XrdScheduler`, `XrdSysThread`, `XrdSysXAttr`, `XrdXrootdGStream`, `XrdCl::URL`, `XrdPosixExtra::FSctl`, `XrdPfcFile`, `XrdPfcInfo`, `XrdPfcIOFile`, `XrdPfcIOFileBlock`, `XrdPfcResourceMonitor`, and `XrdPfcFSctl`. It exports the plugin symbol consumed by XRootD configuration.

## Risks And Edge Cases

- Background write, prefetch, and resource monitor loops run indefinitely and depend on process shutdown for termination.
- `RequestRAM()` increments `m_RAM_used` before `posix_memalign()`; allocation failure returns null without rolling back the budget.
- `GetFile()` sets `errno = res` for negative `Fstat()` values, likely mixing negative errno with positive `errno`.
- `is_http_cache_valid()` parses xattr JSON without local exception handling; malformed xattrs can throw.
- `LocalFilePath()` keeps purge protection by inserting paths into `m_purge_delay_set`; cleanup depends on `ClearPurgeProtectedSet()`.
- `UnlinkFile()` returns `std::min(f_ret, i_ret)`, so mixed success/failure semantics depend on XrdOss return ordering.

## Test Signals

Tests should cover plugin startup without scheduler, decision pass/deny paths, fallback when local file open fails, active-map waiting for concurrent opens, write queue removal during emergency unlink, RAM budget rollback on allocation failure, deferred `Prepare()` with and without `.cinfo`, `LocalFilePath()` completeness and chmod behavior, only-if-cached thresholds, xattr fallback to `.cinfo`, HTTP cache-control revalidation, FSctl eviction integration, and g-stream close record insertion failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfc.cc -->
