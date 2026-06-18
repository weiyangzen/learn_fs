# File Research: sources/os/linux/linux/mm/msync.c

Implementation of `msync(2)` for synchronizing shared file-backed mappings.

Key responsibilities:
- Implements `SYSCALL_DEFINE3(msync)`.
- Validates flags, start alignment, length rounding, overflow, and empty range behavior.
- Walks VMAs overlapping the requested range under mmap read lock.
- Handles unmapped holes according to Linux `msync` behavior.
- For `MS_SYNC`, calls `vfs_fsync_range()` on shared file-backed mapping ranges after taking a file reference and dropping mmap lock.
- Rejects invalidation of locked VMAs with `-EBUSY`.

Important behavior:
- `MS_ASYNC` alone starts no I/O and marks no pages dirty; dirty tracking is handled elsewhere. If the range has holes and only `MS_ASYNC` is requested, it can return `-ENOMEM` immediately.
- Unmapped subranges are skipped but remembered so the syscall can return `-ENOMEM` after syncing mapped portions.
- File offsets are computed from VMA offset plus the virtual offset inside the VMA, and the synced file range is inclusive.
- The function drops mmap read lock around `vfs_fsync_range()` to avoid filesystem sync under mmap lock, then reacquires and resumes VMA lookup.

Dependencies:
- VMA lookup and mmap read lock, VFS file references, `vfs_fsync_range()`, shared mapping flags, tagged-address handling, and `MS_*` user API definitions.

Notable risks:
- Dropping mmap lock around fsync means VMAs may change between iterations; the code restarts lookup at the next virtual address.
- `MS_INVALIDATE` cannot apply to locked VMAs.
- Holes are not fatal until after mapped ranges are processed unless only no-op async behavior remains.
