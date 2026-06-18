# sources/storage-engines/wiredtiger/test/format/checkpoint.c

## Purpose
`checkpoint.c` configures WiredTiger library checkpoints and implements the format checkpoint worker. It tests ordinary checkpoints, named checkpoints, named checkpoint drops, tiered `flush_tier` checkpoints, backup/checkpoint serialization, and checkpoint verification.

## Important APIs, Types, And Functions
It exports `void wts_checkpoints(void)` and `WT_THREAD_RET checkpoint(void *)`. It uses `WT_CONNECTION::reconfigure`, `WT_SESSION::checkpoint`, `wts_verify_mirrors`, `lock_try_writelock`, `lock_writeunlock`, `mmrand`, and config values for checkpoint wait/log size and tiered flush frequency.

## Control Flow
`wts_checkpoints` delays enabling WiredTiger's internal checkpoint server until after initial load, then reconfigures the connection if `checkpoint=wiredtiger`. The worker opens a session and loops until shutdown. Every cycle chooses either `flush_tier`, a named checkpoint, a drop-all named-checkpoint operation, or an unnamed checkpoint. Named checkpoint operations try to acquire `g.backup_lock` so they do not conflict with backup cursor semantics. After checkpoint completion, expected `EBUSY` is tolerated only for cases where named checkpoint metadata can race. Mirrored content is verified at the checkpoint name unless disaggregated storage disables checkpoint cursors.

## State And Persistence Behavior
Checkpoints persist table state and optionally create/drop named snapshots in WiredTiger metadata. Tiered storage flushes object state to the configured storage source. The file does not persist format-side files, but it directly affects recovery and backup visibility.

## Dependencies And Integration Points
The worker depends on `g.checkpoint_config`, `g.tiered_storage_config`, `g.disagg_storage_config`, `g.backup_lock`, and generated configuration values. It coordinates with backup, tiered storage, mirror verification, and disaggregated storage limitations.

## Risks And Test Signals
Risks include checkpoint-induced cache pressure during initial load, backup starvation if locking is wrong, unsupported named checkpoints for tiered/disaggregated tables, and false failures from sweep-server `EBUSY`. Signals include trace start/stop lines with checkpoint config, mirror verification failures, and assertions when unexpected return codes occur.
