# File Research: sources/windows/reactos/drivers/filesystems/btrfs/cache.c

## Purpose

Initializes Windows cache manager callbacks for the Btrfs driver. These callbacks coordinate lazy writer and read-ahead access with the driver's FCB and tree locking rules.

## Main Contents

- Global:
  - `CACHE_MANAGER_CALLBACKS cache_callbacks`.
- Lazy writer callbacks:
  - `acquire_for_lazy_write`
  - `release_from_lazy_write`
- Read-ahead callbacks:
  - `acquire_for_read_ahead`
  - `release_from_read_ahead`
- Initialization:
  - `init_cache`

## Behavior

`acquire_for_lazy_write`:

- Extracts the `fcb` from `FileObject->FsContext`.
- Acquires `Vcb->tree_lock` shared.
- Acquires the file's `Header.Resource` exclusive.
- Records the current thread in `fcb->lazy_writer_thread`.
- Sets top-level IRP to `FSRTL_CACHE_TOP_LEVEL_IRP`.

`release_from_lazy_write`:

- Clears `fcb->lazy_writer_thread`.
- Releases the file resource and tree lock.
- Clears top-level IRP if it is still the cache sentinel.

`acquire_for_read_ahead`:

- Acquires the file resource shared.
- Sets top-level IRP to the cache sentinel.

`release_from_read_ahead`:

- Releases the file resource.
- Clears top-level IRP if appropriate.

`init_cache` installs the four function pointers into `cache_callbacks`.

## Dependencies

- Uses `fcb`, `device_extension`, and tracing macros from `btrfs_drv.h`.
- Uses Windows cache manager callback ABI and resource locking primitives.
- `cache_callbacks` is declared extern in `btrfs_drv.h` for use when cache maps are initialized elsewhere.

## Research Notes

- Lazy-write locking follows the global tree-before-FCB ordering documented in `btrfs_drv.h`.
- Read-ahead does not take the tree lock, only the FCB resource shared.
- Top-level IRP handling is defensive: release callbacks clear only the sentinel value they set.
