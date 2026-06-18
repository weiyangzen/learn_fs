# File Research: sources/os/linux/linux-stable/fs/ocfs2/journal.c

Purpose: implements OCFS2's wrapper around JBD2 journaling, transaction lifecycle, metadata checksum triggers, journal allocation/init/load/shutdown/wipe, commit checkpoint thread, node journal replay/recovery, local-alloc/truncate-log/quota recovery completion, offline replay slot tracking, orphan scanning, and hard-readonly journal checks.

Read coverage: complete file read, 2,479 lines.

Key structures and state:
- `struct ocfs2_replay_map` tracks offline slots needing mount-time replay completion, with states `REPLAY_UNNEEDED`, `REPLAY_NEEDED`, and `REPLAY_DONE`.
- `struct ocfs2_recovery_map` in `journal.h` tracks node numbers queued for recovery.
- `struct ocfs2_la_recovery_item` queues second-phase recovery work: local alloc copy, truncate-log copy, quota recovery object, slot, and orphan recovery mode.
- `trans_inc_lock` serializes journal transaction id increments and metadata-cache transaction markers.

Major logic:
- Recovery initialization sets up recovery mutex/state/thread pointer/waitqueue and allocates a recovery map sized by `max_slots`.
- Replay slot computation marks slots with no node mapping as offline; later, mount recovery queues orphan cleanup for these slots.
- `ocfs2_commit_cache()` blocks new transactions with `j_trans_barrier`, flushes/checkpoints JBD2, increments OCFS2 transaction id, resets outstanding transaction count, wakes downconvert/checkpoint waiters, and reports errors.
- `ocfs2_start_trans()` rejects hard-readonly mounts, starts VFS internal write accounting, takes the transaction barrier, starts a JBD2 handle, and increments outstanding transaction count on clustered mounts.
- `ocfs2_commit_trans()` stops the JBD2 handle and releases barrier/write accounting for non-nested handles.
- Transaction credit helpers extend or restart handles without dropping OCFS2 locks; `ocfs2_allocate_extend_trans()` follows an ext4-style optimistic extension pattern.
- Metadata trigger setup attaches ECC/checksum frozen triggers and abort triggers for dinodes, extent blocks, refcount blocks, group descriptors, directory blocks, xattr blocks, quota blocks, dx roots, and dx leaves.
- `__ocfs2_journal_access()` validates buffer state, fails unsafe write-I/O-error reuse, marks the metadata cache with current transaction id, serializes buffer I/O through cache callbacks, obtains JBD2 write/undo access, and installs ECC triggers.
- `ocfs2_journal_dirty()` wraps `jbd2_journal_dirty_metadata()` and aborts the handle/journal on dirtying failure.
- Journal allocation/init obtains the local journal system inode, locks it with recovery semantics, validates size, creates the JBD2 journal inode object, records dirty state, installs ordered-data callbacks, stores inode/buffer references, and sets mount parameters.
- Journal load calls `jbd2_journal_load()`, clears stored journal errors, optionally flushes after replay, marks the OCFS2 journal dirty, and starts the commit kthread for clustered mounts.
- Journal shutdown stops the commit thread, flushes local journals when needed, destroys JBD2, marks the journal clean only after successful destruction/flush, unlocks and releases the journal inode, and frees the OCFS2 journal object.
- Recovery thread waits for mount, takes the super lock, computes replay slots, queues local orphan cleanup, replays dirty journals of dead nodes, stamps local alloc/truncate-log clean copies, clears recovered slots, refreshes recovery generations, defers quota recovery until safe, queues second-phase cleanup, and exits on disable.
- Journal replay dirty-reads recovery generation first to detect recovery already completed by another node, locks the target journal inode, force-reads cached journal blocks from disk, loads/flushes JBD2, clears dirty flag, bumps recovery generation, writes the dinode, and destroys temporary JBD2 state.
- Dead-node marking reads all journal recovery generations and trylocks remote journal inodes to detect nodes that need recovery.
- Orphan scan periodically takes a cluster-wide orphan scan lock, uses an LVB sequence to avoid duplicate scans across nodes, and queues orphan recovery work for all slots.
- Orphan recovery locks an orphan dir, collects inode references under the dir lock, marks normal orphans as maybe orphaned so `iput()` drives deletion, and handles DIO orphan entries by truncating/removing them under RW and inode locks.
- `ocfs2_check_journals_nolocks()` raw-reads all journal dinodes to refresh recovery generations and returns `-EROFS` if any journal is dirty.

Important entry points:
- Transaction API: `ocfs2_start_trans()`, `ocfs2_commit_trans()`, `ocfs2_extend_trans()`, `ocfs2_assure_trans_credits()`, `ocfs2_allocate_extend_trans()`.
- Journal metadata API: `ocfs2_initialize_journal_triggers()`, `ocfs2_journal_access_*()`, `ocfs2_journal_dirty()`.
- Lifecycle: `ocfs2_journal_alloc()`, `ocfs2_journal_init()`, `ocfs2_journal_load()`, `ocfs2_journal_shutdown()`, `ocfs2_journal_wipe()`.
- Recovery/orphan: `ocfs2_recovery_init()`, `ocfs2_recovery_thread()`, `ocfs2_recovery_exit()`, `ocfs2_mark_dead_nodes()`, `ocfs2_complete_mount_recovery()`, `ocfs2_complete_quota_recovery()`, `ocfs2_orphan_scan_start()`, `ocfs2_orphan_scan_stop()`.

Concurrency and lifetime:
- `j_trans_barrier` prevents checkpoint/shutdown from racing active transactions and also protects cluster-lock transaction ids until commit.
- Recovery state changes are synchronized with `recovery_lock` and `recovery_event`; disable paths wait for running recovery and queued completion work.
- `osb_lock` protects recovery maps, replay maps, orphan wipe counters, and recovery-generation state updates in several paths.
- Second-phase recovery runs on `ocfs2_wq` outside the recovery thread because local alloc/truncate-log/orphan/quota cleanup can take normal cluster locks.
- Orphan recovery advertises per-slot recovery state so `delete_inode()` exits early rather than deadlocking under orphan-dir locks.
- Commit thread loops until shutdown is requested and outstanding transaction count reaches zero.

Important dependencies:
- Wraps JBD2 journal APIs, OCFS2 DLM locks, metadata cache operations, block ECC, journal system inodes, localalloc, truncate log, slot map, quota recovery, orphan directories, inode/file truncation, and workqueues/kthreads.
- Uses Linux buffer cache, page-cache writeback for ordered data, waitqueues, random jitter, and mount write accounting.

Risk and edge cases:
- `ocfs2_commit_cache()` must not drop the transaction barrier while shutdown expects exclusive control.
- Journal replay must force-read blocks because buffer/page cache can hold stale remote journal contents.
- Recovery generation checks avoid double recovery when another node recovered a slot first.
- Dirty journal state is cleared only after JBD2 recovery/flush and dinode write; marking clean too early risks losing metadata replay.
- Orphan scans intentionally include active slots to trigger deletion of inodes held open on nodes that missed unlink notifications.
- `ocfs2_journal_dirty()` aborts aggressively on metadata dirty failures because continuing after journal metadata failure can corrupt the filesystem.
