# File Research: sources/os/linux/linux/io_uring/filetable.c

## Purpose
Implements io_uring fixed-file table allocation, installation, removal, and allocation-range registration.

## Main Functions
- `io_alloc_file_tables()`: allocates resource data and bitmap for registered file slots.
- `io_free_file_tables()`: frees resource data and bitmap.
- `io_file_bitmap_get()`: finds an available slot within the configured allocation range.
- `io_install_fixed_file()`: installs a file into a fixed slot after validation and resource-node allocation.
- `__io_fixed_fd_install()` / `io_fixed_fd_install()`: install a file into a caller-specified or auto-allocated fixed slot.
- `io_fixed_fd_remove()`: removes a fixed file slot and clears its bitmap.
- `io_register_file_alloc_range()`: imports and validates the auto-allocation slot range.

## Important Design Points
- io_uring files themselves cannot be installed as fixed files.
- Userspace fixed slot indices are one-based except `IORING_FILE_INDEX_ALLOC`, which requests automatic allocation.
- Bitmap allocation tracks occupied slots and the next allocation hint.
- File pointer flags are stored in the resource node by `io_fixed_file_set()` from `filetable.h`.

## Cross-File Relationships
- Header helpers are in `filetable.h`.
- Uses resource helpers from `rsrc`.
- Used by open/install fixed-fd operations and cancel paths that resolve fixed files.

## Risks / Review Notes
- `io_fixed_fd_install()` consumes the passed file on error via `fput()`.
- Allocation range validation checks overflow and reserved fields.
- Slot bitmap and resource table must stay synchronized.
