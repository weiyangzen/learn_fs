# File Research: sources/os/linux/linux/fs/configfs/file.c

## Purpose
Implements configfs regular and binary attribute file operations, including open-time permission/callback validation, read/write buffering, binary deferred writes, and attribute dirent creation.

## Main Elements
- `struct configfs_buffer`: per-open state for text/bin attribute callbacks, buffer memory, current count/position, read/write mode flags, item/module references, and max binary size.
- Text reads/writes: `fill_read_buffer()`, `configfs_read_iter()`, `fill_write_buffer()`, `flush_write_buffer()`, and `configfs_write_iter()` implement PAGE-sized text attribute show/store behavior.
- Binary reads: `configfs_bin_read_iter()` first calls the binary read callback with `NULL` to get size, allocates a vmalloc buffer, fills it, then serves user reads.
- Binary writes: `configfs_bin_write_iter()` grows an in-memory buffer and copies user data; `configfs_release_bin_file()` invokes the binary write callback on close.
- Open/release: `__configfs_open_file()` validates live fragments, item/type/callbacks, inode mode, and module owner; `configfs_release()` drops module and buffer resources.
- File operations: `configfs_file_operations` and `configfs_bin_file_operations`.
- Creation helpers: `configfs_create_file()` and `configfs_create_bin_file()` add attribute dirents under an item directory.

## Dependencies And Integration
Attribute access is guarded by the parent dirent fragment semaphore from `dir.c`, which prevents callbacks after teardown. Callback definitions come from `struct configfs_attribute`, `configfs_bin_attribute`, and item type operations.

## Risk Notes
Text writes reject partial-write semantics by sending one copied buffer to `store()`. Binary files do not support switching between read and write modes on the same open. Fragment death returns `-ENOENT`, protecting callbacks during rmdir/unregister; bypassing that would risk use-after-free of client items.
