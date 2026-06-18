# File Research: sources/os/linux/linux/fs/nilfs2/segment.c

`segment.c` is the NILFS segment constructor and log-writer implementation. It coordinates transactions, dirty inode collection, metadata checkpointing, segment allocation, log summary generation, payload block assignment, BIO submission, completion cleanup, GC segment cleaning, and the background `segctord` thread.

The transaction layer stores `struct nilfs_transaction_info` in `current->journal_info`, supports nesting, and serializes ordinary filesystem operations against segment construction using `ns_segctor_sem`. Commits schedule the constructor timer or force synchronous construction depending on flags and dirty pressure.

Log construction is stage-based: GC inodes, dirty files, ifile, cpfile, sufile, DAT, super root, and data-sync stages. `nilfs_segctor_collect_blocks()` advances through these stages, collecting dirty data buffers, btree node buffers, and bmap buffers via operation tables for normal files, DAT, and dsync logs.

Segment buffers are allocated and extended as needed. The constructor marks current/next segments dirty in sufile, allocates additional next segments, writes file-info and block-info entries into segment summaries, assigns physical block numbers through bmaps, finalizes checkpoints, fills the super root, updates segment usage live-block counts, computes checksums, and writes logs.

Write completion clears dirty/writeback/delay/volatile/redirected buffer state, updates `the_nilfs` next-segment cursor, advances checkpoint state when a super root is written, drops collected inode state, and clears metadata dirty bits. Abort paths cancel segment usage, free incomplete allocations, restore freed segments when needed, redirty collected inodes, and preserve consistency after I/O or construction failure.

Public entry points include `nilfs_construct_segment()` for synchronous checkpoint/log construction, `nilfs_construct_dsync_segment()` for data-only fsync-style logs, `nilfs_clean_segments()` for cleaner-driven GC with DAT shadow-map rollback support, and `nilfs_attach_log_writer()`/`nilfs_detach_log_writer()` for lifecycle.

The background `segctord` thread waits on requests, timers, and flush bits, chooses between full checkpoint, file flush, and DAT flush modes, handles freezer integration, and ensures outstanding waiters are awakened during teardown.
