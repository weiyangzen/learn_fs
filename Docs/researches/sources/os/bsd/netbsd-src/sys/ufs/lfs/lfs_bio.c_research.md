# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_bio.c

Read completely: 827 lines.

Implements LFS buffer write interception, resource reservation, cleaner waiting, flush triggering, locked-buffer accounting, and allocation/freeing of LFS-owned I/O buffers.

Global resource accounting:
- Tracks locked-down buffer count/bytes, reserved locked buffer count/bytes, LFS-written pages, per-filesystem page trip threshold, write-in-progress state, and locked-queue waiters.
- Uses `lfs_lock`, `locked_queue_cv`, and `lfs_writing_cv` around these counters.
- Resource thresholds are derived from buffer/page availability via macros in related LFS headers.

Reservation and availability:
- `lfs_reserve()` reserves both estimated disk availability and locked-buffer resources for sensitive vnode-locked operations.
- `lfs_reserveavail()` waits for cleaner progress when available blocks are insufficient, synchronizes cleaner info, wakes the cleaner, and tracks pre-reserved availability.
- `lfs_reservebuf()` forces checkpoint flushes and waits on locked-buffer pressure unless the caller is in a cannot-wait dirop/unlock context.
- `lfs_fits()` estimates whether a requested number of filesystem blocks fits after accounting for summary blocks, dirty inode blocks, segment table, and ifile overhead.
- `lfs_availwait()` wakes and waits for the cleaner until `lfs_fits()` succeeds, with an escape for cleaner/force-checkpoint segment writes.

Write and flush behavior:
- `lfs_bwrite()` is the vnode bwrite entry and delegates to `lfs_bwrite_ext()`.
- `lfs_bwrite_ext()` converts normal buffer writes into delayed locked LFS buffers, marks inodes dirty or cleaner buffers clean, updates availability, reassigns buffers to dirty lists, and suppresses writes on read-only/already-clean filesystems.
- `lfs_flush_fs()` enters the writer, calls `lfs_segwrite()`, clears pending page-daemon flush state, and resets fake availability.
- `lfs_flush()` serializes global flushes, flushes one target filesystem or all mounted LFS filesystems, wakes page waiters, and coordinates with mount busy/unbusy.
- `lfs_needsflush()` and `lfs_needswait()` decide whether resource usage exceeds soft or wait thresholds.
- `lfs_check()` is the pressure gate used before more writes: it may flush dirops, trigger segment writes, wake writerd, and wait for locked-buffer pressure to fall.

Buffer helpers:
- `lfs_newbuf()` allocates an uncached busy I/O buffer, optionally allocates LFS memory, attaches it to a vnode, and sets `lfs_free_aiodone` completion.
- `lfs_freebuf()` detaches the vnode, frees owned memory unless the buffer is fake, and releases the I/O buffer.
- `lfs_wait_pages()` and `lfs_max_pages()` compute dynamic page thresholds from UVM pageable/available memory.

Risks and notes:
- Comments call out missing write-cost accounting, rough reservation estimates, and weak multi-filesystem modeling due to global locked-buffer counters.
- Deadlock avoidance depends on cannot-wait checks for active directory operations and unlock/inactivation paths.
- `lfs_bwrite_ext()` deliberately avoids ordinary asynchronous writes and relies on locked delayed-write buffers so segment writing controls physical placement.
