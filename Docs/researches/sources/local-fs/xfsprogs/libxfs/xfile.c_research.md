# File Research: sources/local-fs/xfsprogs/libxfs/xfile.c

## Role

`xfile.c` implements swappable temporary memory for offline checking and repair. It backs indexed scratch data with memfd or temporary files so large staging datasets can be paged by the kernel instead of requiring resident heap memory.

## Major Responsibilities

- Create close-on-exec scratch file descriptors, preferring `memfd_create`.
- Fall back from `MFD_NOEXEC_SEAL` to plain memfd, then `O_TMPFILE` in `/dev/shm` or `/tmp`, then `mkostemp`.
- Remove unwanted mode bits with `fchmod(0600)`.
- Manage shared file control blocks (`xfile_fcb`) and reference counts.
- Partition a backing fd into page-aligned ranges when callers provide `maxbytes`.
- Load and store data with `pread` and `pwrite`.
- Report actual allocated bytes for private or partitioned xfiles.
- Punch holes with `fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)`.

## File Control Blocks

An `xfile_fcb` owns a file descriptor, refcount, and list linkage. A caller with `maxbytes == 0` receives a private backing file at offset zero. Bounded xfiles are page-rounded and can share a backing fd; `xfile_fcb_find` scans existing fds, extends one if it can append the requested partition, or creates and tracks a new fd.

`xfile_fcb_irele` closes private fcbs without locking. Shared fcbs are refcounted under `fcb_mutex`; the final user removes the fcb and closes the fd. When a non-final user releases the last partition at the end of the file, the backing fd can be truncated down to free address space.

## Load, Store, And Accounting

`xfile_load` treats short reads and out-of-range reads as memory-allocation failures, returning `-ENOMEM`. `xfile_store` treats oversize writes as `-E2BIG`, out-of-partition writes as `-EFBIG`, and short writes as `-ENOMEM`.

`xfile_bytes` returns allocated disk blocks for private xfiles. For partitioned xfiles, `xfile_partition_bytes` walks `SEEK_DATA`/`SEEK_HOLE` within the partition and falls back to `maxbytes` on unexpected seek errors.

## Notable Assumptions

- xfiles are "memory" abstractions, so I/O errors are mapped to memory-style failures where appropriate.
- Callers provide all concurrency control; xfile operations do not lock file ranges.
- Backing files are close-on-exec and intended never to be shared with child processes.
- `xfile_discard` ignores the result of hole punching.
