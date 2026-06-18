# File Research: sources/local-fs/xfsprogs/repair/pptr.h

## Role

`pptr.h` declares the parent pointer repair interface used by phase 6 and metadata repair code.

## Interface

- `parent_ptr_init()` and `parent_ptr_free()` manage global parent-pointer checking state.
- `add_parent_ptr()` records an expected parent pointer from a surviving directory entry.
- `check_parent_ptrs()` scans and repairs on-disk parent pointer xattrs.
- `try_erase_parent_ptrs()` removes parent pointers from an inode, mainly for metadata relinking paths.

## Dependencies

The header assumes libxfs mount and inode types are already available to includers.

## Risk Areas

The interface is intentionally global-state oriented; callers must initialize before recording entries and free only after `check_parent_ptrs()` completes.
