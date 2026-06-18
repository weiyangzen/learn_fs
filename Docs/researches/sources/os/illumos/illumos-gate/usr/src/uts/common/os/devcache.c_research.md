# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devcache.c

## Role

`devcache.c` implements persisted kernel cache-file management for device metadata, usually under `/etc/devices`. Clients register cache files, keep their own in-memory lists, and provide pack/unpack/free callbacks. A background flush daemon serializes dirty in-memory state into nvlist-backed files without blocking the client path that updates device metadata.

The design is explicitly cache-oriented: persisted data must be stateless and regenerable through normal system operation. Examples include device ID caches that help attach a target device directly instead of forcing traversal/attachment of large parts of the device tree.

## Global State and Initialization

The global file lists are:
- `nvf_cache_files`, the normal registered file list;
- `nvf_dirty_files`, a temporary list used while flushing dirty files;
- `nvf_cache_mutex`, protecting list movement.

Flush-daemon state includes timer ID/busy flags, active thread flags, the flush CV/lock, delayed wakeup state, and tunables for write delay and idle exit time. Kernel file I/O reads/writes can be disabled with tunables.

`i_ddi_devices_init()` creates the lists and mutex, then initializes retire-store and devid-cache subsystems. `i_ddi_read_devices_files()` reads the retire store first, then MDI and devid cache files unless reads are disabled. `i_ddi_start_flush_daemon()` initializes daemon synchronization and wakes the daemon if any registered file is already dirty. `i_ddi_clean_devices_files()` cleans devid and MDI caches.

## Registration and Client Interface

`nvf_register_file()` allocates an `nvfd_t`, stores operation callbacks, initializes the per-file rwlock, inserts it into the global cache-file list, and returns an opaque handle. There is no unregister path.

Client helpers expose:
- `nvf_cache_name()` for the backing path;
- `nvf_lock()` for the per-file rwlock;
- `nvf_list()` for the client-owned data list;
- `nvf_mark_dirty()` and `nvf_is_dirty()` with assertions that the caller holds the lock in the required mode.

The file-level lock must be held as reader for traversal/state checks and writer for list mutation, dirty marking, reads, pack, unpack, and free-list callbacks.

## File Format and Read Path

Persisted files contain an `nvpf_hdr_t` followed by a packed native nvlist. `nvp_cksum()` computes a simple XOR checksum over 16-bit words, with odd trailing byte handling.

`fread_nvlist()` opens the file through `kobj_open_file()`, reads and validates the header magic/version/header checksum, reads the nvlist payload, verifies there is no trailing data, validates payload checksum, unpacks the nvlist, and returns it. It maps missing files to `ENOENT`, I/O errors to `EIO`, and malformed/corrupt data to `EINVAL`.

`fread_nvp_list()` walks the top-level nvlist. Each top-level pair must be a nested nvlist; the pair name identifies the cached element. It calls the client's unpack callback for each sublist while holding the file write lock. Unsupported types or unpack errors invalidate the partially built list by calling the client's free-list callback.

`nvf_read_file()` wraps this read path, respects global read-disable, and sets flags that later produce create/rebuild messages depending on whether the file was missing, corrupt, or unreadable.

## Kernel File I/O and Write Path

Low-level helpers wrap vnode operations:
- `kfcreate()` opens a file with create/write/truncate;
- `kfremove()` removes a file;
- `kfread()` and `kfwrite()` use `vn_rdwr()` and track file position/state;
- `kfclose()` fsyncs writable files before closing and releases the vnode;
- `kfrename()` atomically renames a temporary file over the target.

`fwrite_nvlist()` packs an nvlist, builds a checked header plus payload buffer, writes to `filename.new`, fsyncs/closes it, removes it on error, and renames it over the target on success. This temp-file-plus-rename protocol reduces the chance of cache-file data loss.

`e_fwrite_nvlist()` wraps write status into DDI return codes and marks a file read-only if the write failed with `EROFS`.

## Flush Scheduling and Daemon

`nvf_wake_daemon()` is called after dirtying a cache. It does nothing until I/O is initialized or during shutdown. Otherwise it starts the daemon thread if inactive, computes a delayed flush deadline, and arms a timeout when one is not already active. Repeated updates push `nvpticks` later so bursty device changes are coalesced.

`nvpflush_timeout()` either re-arms itself if the target deadline is still more than four ticks away or signals the daemon to flush.

`nvpflush_one()` handles one file. It obtains the file rwlock, skips clean/read-only/write-disabled/shutdown files, upgrades to writer, asks the client to pack the list into an nvlist, clears dirty and marks flushing, writes the nvlist without holding the file lock, then clears flushing and updates flags. Failed writable updates set error and dirty flags for retry. Read-only failures are silently treated as success. If the file was dirtied while the write was in progress, it returns failure so the daemon will schedule another flush.

`nvpflush_daemon()` waits for flush requests or idle timeout, exits when idle with no pending timer or on shutdown, moves dirty files from the main list to the dirty list, flushes them without holding the global list lock, moves clean files back, invokes write-complete callbacks, and reschedules itself when a file remains dirty or a write fails.

## Locking and Failure Behavior

The implementation separates global list locking from per-file data locking. Dirty files are moved to `nvf_dirty_files` so the daemon does not hold `nvf_cache_mutex` across packing or kernel file I/O. Packing and unpacking callbacks are called with the per-file write lock held and are expected to return with it still held.

Write failures are retried after delay unless the backing filesystem is read-only. Corrupt or missing files are not fatal because caches are expected to be rebuilt.

## Subset Relevance

This file is directly relevant to device discovery and persistent device metadata, including caches used by storage identity paths. It supports faster device attachment and stable metadata reconstruction for block/storage devices that filesystems depend on.
