# File Research: sources/os/linux/linux/io_uring/filetable.h

## Purpose
Defines io_uring fixed-file table APIs and inline slot/flag helpers.

## Main Contents
- Prototypes for file table allocation/free, fixed fd install/remove, allocation-range registration, and `io_file_get_flags()`.
- Bitmap helpers:
  - `io_file_bitmap_clear()`
  - `io_file_bitmap_set()`
- Encoded slot flags:
  - `FFS_NOWAIT`
  - `FFS_ISREG`
  - `FFS_MASK`
- Slot helpers:
  - `io_slot_flags()`
  - `io_slot_file()`
  - `io_fixed_file_set()`
  - `io_file_table_set_alloc_range()`

## Important Design Points
- Low bits of `node->file_ptr` encode fixed-file capability flags; the masked value is the actual `struct file *`.
- `io_slot_flags()` maps stored file flags into request flag positions starting at `REQ_F_SUPPORT_NOWAIT_BIT`.
- Bitmap helpers update `alloc_hint` to speed subsequent allocation.

## Cross-File Relationships
- Implemented by `filetable.c`.
- `io_file_get_flags()` is provided by io_uring core and feeds fixed-file capability encoding.
- Used by cancellation, fdinfo, openclose, and resource paths.

## Risks / Review Notes
- Pointer tagging assumes file pointer alignment leaves low bits free.
- `FFS_MASK` is an inverse mask; helper usage must preserve the intended pointer/flag split.
