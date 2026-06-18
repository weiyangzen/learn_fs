# File Research: sources/os/linux/linux/fs/ocfs2/journal.c

`journal.c` implements OCFS2’s JBD2 integration and clustered recovery machinery. It covers transaction handles, metadata checksum triggers, journal load/shutdown/wipe, commit thread behavior, node recovery, replay slot tracking, local alloc/truncate/quota recovery handoff, and orphan directory recovery.

Main responsibilities:
- Maintains replay maps for offline slots, allowing recovery of slots that have no active node mapping.
- Initializes, disables, and exits recovery state through `ocfs2_recovery_init()`, `ocfs2_recovery_disable*()`, and `ocfs2_recovery_exit()`.
- Tracks nodes needing recovery in `ocfs2_recovery_map`, guarded by `osb_lock` and `recovery_lock`.
- Implements `ocfs2_commit_cache()` to flush JBD2, increment OCFS2 transaction IDs, reset transaction counts, wake downconvert/checkpoint waiters, and serialize with `j_trans_barrier`.
- Implements transaction APIs:
  - `ocfs2_start_trans()` checks readonly state, starts sb internal write, takes transaction barrier, starts JBD2 handle, and counts active transactions for clustered mounts.
  - `ocfs2_commit_trans()` stops JBD2 and releases barriers for non-nested handles.
  - `ocfs2_extend_trans()`, `ocfs2_assure_trans_credits()`, and `ocfs2_allocate_extend_trans()` manage handle credit growth/restart.
- Sets up JBD2 frozen/abort triggers for dinodes, extent blocks, refcount blocks, group descriptors, directory blocks, xattr blocks, quota blocks, dx roots, and dx leaves so metadata ECC is computed at journal freeze time.
- Provides typed `ocfs2_journal_access_*()` wrappers that set the correct checksum trigger and call JBD2 write/undo access under metadata-cache I/O locking.
- Implements `ocfs2_journal_dirty()` with abort handling if JBD2 dirtying fails.
- Allocates, initializes, loads, shuts down, and wipes journals:
  - `ocfs2_journal_alloc()` creates the OCFS2 journal skeleton.
  - `ocfs2_journal_init()` opens the slot journal system inode, locks it, creates the JBD2 journal, records dirty state, and installs data-buffer callbacks.
  - `ocfs2_journal_load()` loads JBD2, clears recorded errors, marks OCFS2 journal dirty, and starts the commit thread for clustered mounts.
  - `ocfs2_journal_shutdown()` stops commit thread, flushes/destroys JBD2, clears dirty state if safe, unlocks/releases the journal inode, and frees journal state.
- Implements recovery:
  - Forces journal data reread from disk before replay to avoid stale cached blocks.
  - Replays dirty remote slot journals, clears dirty flags, increments recovery generation, and writes journal dinode ECC.
  - Recovers dead nodes by replaying journals, stamping local alloc/truncate log clean, clearing slot ownership, and queuing second-phase cleanup.
  - Detects dead nodes at mount by trylocking journal inodes and recording recovery generations.
- Implements second-phase recovery work:
  - Cleans recovered local alloc windows.
  - Completes truncate log cleanup.
  - Recovers quotas after other recovery work.
  - Scans orphan directories and iputs queued orphan inodes so normal eviction/delete paths finish cleanup.
- Implements periodic orphan scans for clustered mounts using delayed work and an orphan scan lock/sequence number so only one node scans all orphan dirs per interval.
- Provides hard-readonly journal checks via `ocfs2_check_journals_nolocks()`.

Key invariants:
- OCFS2 transaction IDs are separate from JBD2 tids and are used by lock/cache checkpoint decisions.
- Metadata buffers must go through journal access before dirtying.
- Recovery generation prevents duplicate recovery when another node already recovered a slot.
- Journal replay is the authoritative first phase of node recovery; local alloc, truncate log, quota, and orphan cleanup are queued after the node can be considered safely recovered.
- Orphan recovery coordinates with `inode.c` delete paths to avoid deadlocks and duplicate inode wiping.
