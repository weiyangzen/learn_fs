# File Research: sources/os/linux/linux/fs/nilfs2/segment.h

`segment.h` defines the public structures and interfaces for NILFS recovery and segment construction. `struct nilfs_recovery_info` stores search/recovery state: recovery flags, latest super-root block/checkpoint, roll-forward range, starting sequence, used-segment list, last partial segment location, sequence, segment number, and next segment number.

`struct nilfs_cstage` tracks the segment constructor’s collection stage, including the stage counter, collection flags, current dirty-file pointer, and current GC-inode pointer. Stage transitions are instrumented from `segment.c`.

`struct nilfs_sc_info` is the complete segment-constructor state object. It stores root/superblock pointers, dirty and GC inode lists, deferred iput work, segments to free, dsync target/range, active and writing segment-buffer lists, summary write cursors, block counters, checkpoint and time state, constructor flags, wait queues, request sequence counters, flush state, timer, thread pointer, interval, checkpoint frequency, and watermark.

The header defines constructor flags (`NILFS_SC_DIRTY`, `NILFS_SC_UNCLOSED`, `NILFS_SC_SUPER_ROOT`, `NILFS_SC_PRIOR_FLUSH`, `NILFS_SC_HAVE_DELTA`), request state (`NILFS_SEGCTOR_COMMIT`), cleanup retry count, default constructor timeout, super-root frequency, and dirty-buffer watermark.

Declared interfaces connect superblock/recovery code to segment construction: synchronous segment construction, dsync construction, cleaner segment cleaning, log-writer attach/detach, super-root search, roll-forward salvage, and segment-list disposal.
