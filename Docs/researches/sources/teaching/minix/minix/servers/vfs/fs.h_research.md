# File Research: sources/teaching/minix/minix/servers/vfs/fs.h

Master include header for VFS source files.

Key contents:
- Defines `_SYSTEM`.
- Includes MINIX configuration, core types, device-map, DS/RS, call numbers, system libraries, timers, and common libc headers.
- Includes VFS-local headers:
  - `const.h`
  - `dmap.h`
  - `proto.h`
  - `threads.h`
  - `glo.h`
  - `type.h`
  - `vmnt.h`
  - `fproc.h`

This header centralizes the VFS compilation environment and shared internal declarations.
