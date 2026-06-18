# File Research: sources/os/bsd/netbsd-src/sys/sys/filedesc.h

Read completely: 265 lines.

## Purpose
Defines process file descriptor tables, per-descriptor state, current/root directory state, and kernel descriptor-management APIs.

## Main Interfaces
- Sizing constants: `NDFILE`, `NDEXTENT`, `NDENTRIES`, bitmap helpers.
- `fdfile_t`: per-descriptor close-on-exec/fork flags, allocation state, refcount, file pointer, knotes, close cv.
- `fdtab_t`: active descriptor table.
- `filedesc_t`: built-in descriptors, lock, active table pointer, bitmaps, knote hash, high-water marks, refcount, close flags, built-in table/maps.
- `cwdinfo_t`: current/root/emulation root vnodes, umask, refcount, rwlock.
- Kernel APIs: descriptor allocation, duplication, sharing/copying/freeing, close-on-exec/fork, fd lookup/put, vnode/socket lookup, close, clone, pipe, cwd management, path reconstruction, `closef`, fcntl lock helper.

## Dependencies And Integration
Includes locks, queues, vnode pointers, knotes, file objects, process/lwp state, and path helpers. It is used by open/close, fork/exec, kqueue, VFS lookup, and socket/file operations.

## Risks And Edge Cases
- Close-on-exec/fork flags should be set via `fd_set_exclose`/`fd_set_foclose` to keep summary booleans consistent.
- Descriptor tables can be shared by multiple processes and have active-table replacement.
- Refcount high bit `FR_CLOSING` marks closing interlock state.
- Built-in descriptors have strict cache-line alignment.

## Filesystem Relevance
High. Every open file, directory fd, `*at` syscall, cwd/root, and vnode descriptor path depends on this structure.
