# File Research: sources/os/linux/linux/fs/gfs2/recovery.c

Implements journal replay and recovery work for dirty GFS2 journals. It reads journal blocks, manages replay revokes, validates log headers, scans descriptors through log operations, updates statfs state, writes clean journal headers, and reports recovery results to the lock manager.

Key exported functions include `gfs2_replay_read_block`, `gfs2_revoke_add`, `gfs2_revoke_check`, `gfs2_revoke_clean`, `__get_log_header`, `gfs2_recover_func`, `gfs2_recover_journal`, and `gfs2_log_pointers_init`.

Important behavior:
- `gfs2_replay_read_block()` maps journal logical blocks to disk blocks and reads metadata with readahead.
- Revoke tracking records the latest revoke position for a block and checks whether a replay block falls before/after the revoke across circular journal wrap.
- `__get_log_header()` validates magic/type/block number, legacy hash, CRC, and extracts sequence, flags, tail, block number, and local statfs deltas.
- `foreach_descriptor()` walks active journal descriptors from tail to head, tolerates embedded log headers, validates descriptor metadata, and dispatches scan handlers for each replay pass.
- Recovery uses two passes: pass 0 collects revokes; pass 1 replays metadata and journaled data not revoked.
- `recover_local_statfs()` applies journal-header local statfs deltas to the master statfs inode and zeroes the recovered journal's local statfs inode.
- `clean_journal()` writes an unmount/recovery log header to mark replay complete.
- `gfs2_recover_func()` acquires journal locks for remote journals, checks read-only/frozen constraints, runs replay under `sd_log_flush_lock`, initializes log pointers for this node's own journal, emits uevents, and reports success or gave-up status to the lock manager.
- `gfs2_recover_journal()` queues recovery work and optionally waits for completion.
- `gfs2_log_pointers_init()` sets log sequence/head/tail/flush pointers from the discovered journal head.

Risk areas include replay under freeze/read-only conditions, circular revoke math, descriptor scan bounds, statfs recovery idempotence, and coordinating remote journal locks with DLM recovery.
