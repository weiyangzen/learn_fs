# sources/storage-engines/wiredtiger/test/suite/test_tiered06.py

## Purpose
`test_tiered06.py` directly tests WiredTiger storage-source and customized file-system APIs used internally by tiered storage.

## Important APIs, Types, and Functions
The class exposes helpers `get_storage_source`, `get_fs_config`, `suffix`, `check_dirlist`, `check_home`, `check_local_objects`, and `create_wt_file`. It uses `wiredtiger.StorageSource`, `wiredtiger.FileSystem`, `ss_customize_file_system`, `ss_flush`, `ss_flush_finish`, `fs_directory_list`, `fs_exist`, `fs_open_file`, `fh_read`, `fs_size`, `fh_size`, `fh_lock`, `fs_rename`, and `fs_remove`.

## Control Flow
`test_ss_basic` customizes a file system, verifies nonexistence, creates a local file, flushes it to the store, reads it back, checks size and locking, tests bad open, rename, remove, and termination behavior. `test_ss_write_read` writes a large file non-sequentially, flushes it, and validates random and backward reads. `test_ss_file_systems` creates independent file systems for different buckets/cache directories, checks bad bucket errors, flushes multiple files, verifies prefix directory listing, duplicate flush behavior for local storage, and termination independence.

## State and Persistence Behavior
The tests distinguish local WT home files, cache-directory copies, and shared bucket objects. Directory-store checks map "cloud" state to bucket directories.

## Dependencies and Integration Points
It integrates with storage-source extension entry points, file-handle read/size APIs, Python filesystem operations, error-pattern helpers, and tiered scenario setup.

## Risks and Test Signals
Risks include overwrite policy gaps for non-local stores, cache assumptions, and provider-specific error messages. Signals are exact directory listings, byte-for-byte block checks, expected exceptions, and successful termination.
