# File Research: sources/windows/winbtrfs/src/cache.c

## Role

`cache.c` installs WinBtrfs cache manager callbacks for lazy writer and read-ahead paths.

## Behavior

- Defines the global `CACHE_MANAGER_CALLBACKS cache_callbacks`.
- `acquire_for_lazy_write`:
  - Converts `Context` to `PFILE_OBJECT`, then to `fcb`.
  - Acquires `fcb->Vcb->tree_lock` shared.
  - Acquires the FCB header resource exclusive.
  - Records `fcb->lazy_writer_thread`.
  - Sets top-level IRP to `FSRTL_CACHE_TOP_LEVEL_IRP`.
- `release_from_lazy_write`:
  - Clears `lazy_writer_thread`.
  - Releases the FCB resource and then `tree_lock`.
  - Clears top-level IRP if it still equals the cache top-level marker.
- `acquire_for_read_ahead`:
  - Acquires the FCB resource shared.
  - Sets top-level IRP to cache top-level marker.
- `release_from_read_ahead`:
  - Releases the FCB resource.
  - Clears the top-level IRP marker if still present.
- `init_cache` wires these four callbacks into `cache_callbacks`.

## Dependencies

- Includes `btrfs_drv.h` for FCB/VCB structures, `TRACE`, and Windows kernel types.
- Used where `CcInitializeCacheMap` receives `&cache_callbacks`.

## Research Notes

- Lazy writer takes `tree_lock` before the FCB resource, matching the broader lock-order discipline in the driver.
- Lazy writer uses exclusive FCB resource acquisition, while read-ahead uses shared acquisition.
- The callbacks respect the cache manager's nonblocking `Wait` parameter by returning `false` if either required resource cannot be acquired.
