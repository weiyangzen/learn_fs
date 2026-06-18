# File Research: sources/os/bsd/freebsd-src/sys/sys/_rmlock.h

Mostly-reader lock structure definitions.

Key elements:
- Defines reader queue structures, `struct rmlock`, `struct rm_priotracker`, and `struct rmslock`.
- `struct rmlock` embeds common lock metadata, writer CPU set state, active reader list, and a union of write-lock representations.
- Provides field aliases for union members.

Dependencies:
- Includes cpuset, lock, mutex, queue, and sx headers.

Research notes:
- Supports read-mostly concurrency patterns common in routing, VFS, and global kernel state.
- `rm_priotracker` keeps per-reader priority/thread tracking.
