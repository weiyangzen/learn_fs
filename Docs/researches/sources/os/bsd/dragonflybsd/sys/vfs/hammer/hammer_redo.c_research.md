# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_redo.c

Purpose: generates REDO records in the shared UNDO/REDO FIFO for HAMMER version 4+ fsync acceleration and crash recovery.

Main generator: `hammer_generate_redo()` appends one or more REDO records under `undo_lock`, wrapping the FIFO as needed and preformatting new FIFO buffers. It handles insufficient aligned space by writing PAD records, writes sequence-numbered and CRC-protected REDO records, appends a tail, and writes a dummy PAD up to the next alignment point so recovery can scan without trusting volume-header indices.

Inode tracking: for inode-related REDOs, the first active FIFO offset is stored in `ip->redo_fifo_start`, and the inode is inserted into `hmp->rb_redo_root` under `HAMMER_INODE_RDIRTY`. `redo_fifo_next` tracks the next earliest REDO while an inode is being flushed to the backend.

SYNC records: `hammer_generate_redo_sync()` emits `HAMMER_REDO_SYNC` containing the earliest active REDO FIFO offset. During REDO recovery it reuses the original recovery extended offset so a second crash can rerun the same logical REDOs. Normal UNDO generation forces at least one SYNC record into the nominal recovery span.

Flush hooks: `hammer_redo_fifo_start_flush()` clears `redo_fifo_next` as an inode begins backend flush. `hammer_redo_fifo_end_flush()` removes stale RDIRTY state, clears tracking when no dirty buffers remain, or reinserts the inode with `redo_fifo_start = redo_fifo_next`.

Research notes: this file mirrors much of the FIFO layout logic in `hammer_undo.c`; the difference is logical operation replay rather than raw block restoration. Correct RB ordering by earliest FIFO offset is essential because stage2 recovery uses the minimum active REDO offset.
