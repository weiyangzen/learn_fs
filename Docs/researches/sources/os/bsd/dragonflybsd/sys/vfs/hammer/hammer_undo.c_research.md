# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_undo.c

Purpose: manages the UNDO side of the shared UNDO/REDO FIFO and the recent-UNDO history cache.

Offset lookup: `hammer_undo_lookup()` converts a zone-3 UNDO offset into the underlying zone-2 buffer offset through the root volume's undo translation.

UNDO generation: `hammer_generate_undo()` ensures a REDO_SYNC exists for version 4+ filesystems, checks recent undo history to avoid duplicate coverage, locks the FIFO, verifies space, appends one or more UNDO records, and writes PAD records when alignment leaves no room for payload. Each UNDO record stores the target raw zone offset and a copy of original bytes; records have sequence numbers, tails, and CRCs.

FIFO formatting and upgrade: `hammer_format_undo()` preformats a new FIFO buffer with DUMMY records on every 512-byte alignment unit so recovery can detect stale or missed writes. `hammer_upgrade_undo_4()` converts pre-version-4 undo space by resetting first/next offsets and writing DUMMY entries with sequence numbers across the entire undo area.

History cache: `hammer_enter_undo_history()` stores recent offset/length ranges in an RB tree plus LRU list and returns `EALREADY` when a new request is fully covered by an existing undo. `hammer_clear_undo_history()` resets that cache.

Space accounting: `hammer_undo_used()`, `hammer_undo_space()`, and `hammer_undo_max()` compute FIFO usage using the in-core next offset and on-disk first offset, including space reserved from the previous flush. `hammer_undo_reclaim()` keeps the current append buffer resident and permits reclaim of other undo buffers.

Research notes: UNDO records are raw physical restorations replayed backward by recovery. The history cache is an optimization only; correctness still depends on generating the first UNDO before modifying any raw metadata bytes.
