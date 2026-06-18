# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_flusher.c

## Role

Implements HAMMER’s dependency flusher: a master thread sequences flush groups, slave threads flush dirty inodes, and finalization synchronizes data, UNDO/REDO, volume headers, metadata, and delayed frees.

## Thread Model

- `hammer_flusher_create()` starts one master thread and `HAMMER_MAX_FLUSHERS` slave threads.
- `hammer_flusher_destroy()` shuts down the master, then drains and stops idle slaves.
- `hammer_flusher_master_thread()` owns sequence advancement, loose I/O cleanup, group flushing, completion wakeups, and idle waiting.
- `hammer_flusher_slave_thread()` scans the current flush group’s RB tree and calls `hammer_flusher_flush_inode()` for available inodes.

## Flush Group APIs

- `hammer_flusher_sync()` closes pending groups and waits for completion.
- `hammer_flusher_async()` closes groups up to a target group, signals the master, and returns the relevant sequence number.
- `hammer_flusher_async_one()` flushes the current/next flushable group or creates a dummy sequence for FIFO/metadata-only work.
- `hammer_flusher_wait()` sleeps until a sequence number is complete.
- `hammer_flusher_running()` reports whether pending sequence numbers remain.
- `hammer_flusher_wait_next()` combines async-one and wait.

## Core Flush Flow

`hammer_flusher_flush()` processes one sequence number:

- Finds the next flush group matching `done + 1`.
- Starts a flusher transaction.
- If undo space is already too low, finalizes a dummy cycle first to move undo FIFO state forward.
- Assigns the flush group and transaction copy to all ready slaves.
- Waits until every slave returns to the ready list.
- Calls `hammer_flusher_finalize()` for final synchronization.
- Removes the flush group when its tree is empty.
- Runs metadata/FIFO-only finalization when there is work but no inode group.
- Clears delayed reservations whose safe sequence has arrived.

## Inode Flush Worker

`hammer_flusher_flush_inode()`:

- Uses `HAMMER_INODE_SLAVEFLUSH` to prevent multiple slaves from flushing the same inode concurrently.
- Cleans loose I/O and waits for VM pressure to become nominal.
- Calls `hammer_sync_inode()`.
- Treats `EWOULDBLOCK` as a normal retry condition and converts other errors into serious inode sync errors through completion handling.
- Calls `hammer_sync_inode_done()`.
- Finalizes when undo space is below emergency level or metadata dirty space exceeds the configured limit.

## Finalization

`hammer_flusher_finalize()` performs the durability sequence:

- Serializes finalization with `finalize_lock`.
- Flushes dirty data buffers first.
- Takes the sync lock exclusively before metadata/UNDO-sensitive operations.
- On final cycles, copies cached blockmaps into the root volume and generates undo-protected modifications.
- Saves the undo append point, flushes UNDOs, and updates on-disk undo FIFO pointers when needed.
- Updates and flushes `vol0_next_tid` without undo so TIDs are not reused after rollback.
- For pre-version-4 filesystems, waits for I/O because recovery depends on the volume header update.
- Flushes metadata asynchronously after undo is safe.
- On final cycles, advances cached undo `first_offset`, clears undo history, advances flush TID state, and clears redo sync state.

## Pressure and Work Detection

- `hammer_flusher_undo_exhausted()` reports undo space below a quarter threshold chosen by caller.
- `hammer_flusher_meta_limit()` and `hammer_flusher_meta_halflimit()` guard dirty metadata pressure.
- `hammer_flusher_haswork()` checks dirty inodes, dirty volume/undo/data/meta roots, and pending undo FIFO synchronization.
- `hammer_flush_dirty()` repeatedly syncs while work remains, with a max-count escape.

## Research Notes

This file coordinates HAMMER’s crash-consistency protocol. The key design is that metadata can flush asynchronously only after corresponding UNDO state is durable enough for recovery, while data writes are handled separately because HAMMER does not overwrite file data in the same way.
