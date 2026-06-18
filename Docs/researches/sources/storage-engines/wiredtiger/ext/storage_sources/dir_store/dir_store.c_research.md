# sources/storage-engines/wiredtiger/ext/storage_sources/dir_store/dir_store.c

## Purpose
This file implements the `dir_store` WiredTiger storage source extension. It is a demonstration and test storage source that treats local directories as a stand-in for cloud object storage, with an optional read cache directory and configurable artificial delay/error injection.

## Important APIs, Types, and Functions
The main extension type is `DIR_STORE`, whose first field is `WT_STORAGE_SOURCE`, so it can be registered through `WT_CONNECTION->add_storage_source`. `DIR_STORE_FILE_SYSTEM` wraps WiredTiger's native `WT_FILE_SYSTEM` while tracking bucket/cache/home directories. `DIR_STORE_FILE_HANDLE` wraps a real `WT_FILE_HANDLE` and is tracked in a `TAILQ`.

Key storage-source entry points are `dir_store_customize_file_system`, `dir_store_flush`, `dir_store_flush_finish`, `dir_store_add_reference`, and `dir_store_terminate`. File-system entry points include `dir_store_open`, `dir_store_exist`, `dir_store_size`, `dir_store_remove`, `dir_store_rename`, and directory-list helpers. File-handle methods forward reads and size calls to the underlying handle while rejecting writes.

## Control Flow
`wiredtiger_extension_init` allocates and initializes `DIR_STORE`, installs the storage-source vtable, parses extension config values, and registers the name `dir_store`. A connection later calls `ss_customize_file_system`, which parses `cache_directory`, obtains the native file system, resolves bucket/cache directories relative to the WiredTiger home, and returns a customized `WT_FILE_SYSTEM`.

On flush, the extension maps the source name to the home directory and the object name to the bucket directory, optionally delays/fails through `dir_store_delay`, then copies via `dir_store_file_copy` using a `*.TMP` temporary file and exclusive create before rename. `flush_finish` optionally hard-links the just-flushed source into the cache and makes it read-only. Opens are read-only only; if caching is enabled, `dir_store_open` copies missing bucket objects into the cache before opening the cached copy.

## State and Persistence Behavior
Persistent objects are ordinary files in `bucket_dir`; cached objects are ordinary files in `cache_dir`; source files come from `home_dir`. `dir_store_file_copy` makes destination objects read-only and avoids overwriting existing objects. Object-read/write counters and operation counters are in-memory only and are used for simulated delay/error behavior. The file handle queue is protected by `file_handle_lock`; the storage source itself uses a reference count so termination frees the shared object only after all references are released.

## Dependencies and Integration Points
The file depends on WiredTiger extension interfaces from `wiredtiger.h` and `wiredtiger_ext.h`, internal helper macros from `wt_internal.h`, POSIX filesystem calls, pthread rwlocks, and the local `queue.h`. It integrates with WiredTiger as a named storage source and with the native file system via `WT_EXTENSION_API->file_system_get`.

## Risks and Edge Cases
The implementation is POSIX-centric: it uses `link`, `chmod`, `stat`, `opendir`, pthread locks, and Unix path semantics. `dir_store_path` strips leading `./` variants but does not fully normalize paths. Cache population races are only partially tolerated through temporary/exclusive copy behavior. Hard-link based caching can fail across file systems. Artificial counters are mostly unsynchronized except for targeted TSAN suppressions. Rename is unsupported, and writes through opened object handles return `ENOTSUP`.

## Test Signals
Useful tests exercise extension loading, custom file-system creation, read-only open behavior, flush and flush_finish, cache hit/miss paths, directory listing with directory/prefix filters, object removal from both cache and bucket, delay/error config, and multi-handle close/termination cleanup. Recovery-style tests should verify that copied bucket objects are immutable and that partial temporary copies are removed after errors.
