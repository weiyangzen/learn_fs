# File Research: sources/os/bsd/freebsd-src/sys/sys/priority.h

This header defines FreeBSD scheduler priority classes and numeric ranges. Classes include interrupt thread, realtime, timeshare, and idle. `PRI_FIFO` overlays a FIFO bit on realtime priority, and helper macros extract the base class, test realtime, and decide whether round-robin behavior is needed.

The priority number space is 0 to 255, where lower values are higher priority. Ranges are reserved for interrupt threads, realtime user threads, kernel threads, timeshare user threads, and idle user threads. Constants define representative interrupt priorities, kernel sleep priorities (`PSWP`, `PVM`, `PINOD`, `PRIBIO`, `PVFS`, `PZERO`, etc.), and user/idle range boundaries. Kernel-only `PRI_USER` and `PRI_UNCHANGED` are arguments to yield behavior.

`struct priority` stores scheduling class, normal priority level, native priority before propagation, and user priority derived from CPU/nice accounting. Filesystem relevance is practical: I/O wait priorities, VFS sleep priority (`PVFS`), inode priority (`PINOD`), and buffer I/O priority (`PRIBIO`) influence scheduling latency in filesystem paths.
