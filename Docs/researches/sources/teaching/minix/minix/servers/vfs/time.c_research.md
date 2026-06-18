# File Research: sources/teaching/minix/minix/servers/vfs/time.c

## Purpose
Implements `do_utimens`, covering timestamp updates for named paths and file descriptors.

## Main Entry Point
- `do_utimens()` handles `utimens`, `lutimens`, `utimensat` absolute/`AT_FDCWD` cases, and `futimens`.

## Control Flow
The function reads requested atime/mtime from `job_m_in.m_vfs_utimens`. If a name is present, it validates flags, chooses symlink-follow behavior, resolves the path with `eat_path`, and locks the vnode/vmnt for reading. If no name is present, it treats the request as fd-based and uses `get_filp`.

It checks ownership/superuser authorization, allows `UTIME_NOW`/`UTIME_NOW` touch through write permission, rejects read-only mounts, materializes `UTIME_NOW` with `clock_time`, preserves `UTIME_OMIT`, validates nanoseconds, and sends the final request to the file server through `req_utime`.

## Dependencies
Uses path resolution, filp lookup, vnode/vmnt locking, `forbidden`, `read_only`, `clock_time`, and FS request helper `req_utime`.

## Limitations
The header comment explicitly says relative `utimensat(fd, "some/path", ...)` is not implemented.

## Risks and Notes
The code carefully unlocks either the temporary path vnode/vmnt or the fd filp depending on call style. It supplies sensible seconds values for `UTIME_OMIT` to accommodate older file servers.
