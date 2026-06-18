# File Research: sources/os/linux/linux/fs/proc/fd.h

## Purpose
Internal procfs header declaring fd/fdinfo operations and helper accessors used by per-process procfs code.

## Main Contents
- Extern declarations for:
  - `proc_fd_operations`
  - `proc_fd_inode_operations`
  - `proc_fdinfo_operations`
  - `proc_fdinfo_inode_operations`
  - `proc_fd_permission()`
- Inline helper `proc_fd()` returning `PROC_I(inode)->fd`.

## Dependencies and Integration
Includes `linux/fs.h` and relies on proc inode internals through `PROC_I`. Used by `base.c` to wire `/proc/<pid>/fd`, `/fdinfo`, and `map_files` permissions, and by `fd.c` for implementation.

## Risks and Review Hotspots
- `proc_fd()` assumes the inode is a proc inode with a valid fd field.
- The shared `proc_fd_permission()` is used outside `fd.c`, so behavior changes affect multiple procfs directories.
