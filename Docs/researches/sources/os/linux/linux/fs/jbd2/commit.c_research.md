# File Research: sources/os/linux/linux/fs/jbd2/commit.c

Implements the full JBD2 transaction commit path.

Support helpers:
- `journal_end_buffer_io_sync()` completes journal bio writes for temporary buffer_heads and wakes any shadowed original buffer.
- `release_buffer_page()` attempts to strip buffers from truncated, unmapped folios after forget-list processing.
- Checksum helpers set commit-block checksums, descriptor tag checksums, and data CRCs.
- `journal_submit_commit_record()` allocates and writes the commit block, adding timestamps, checksums, and PREFLUSH/FUA when barriers require it.
- `journal_wait_on_commit_record()` waits for commit block I/O and returns `-EIO` on failure.

Data=ordered inode handling:
- `jbd2_submit_inode_data()` and `jbd2_wait_inode_data()` are exported helpers for individual journaled inodes.
- `journal_submit_data_buffers()` walks committing transaction inode list, marks each inode `JI_COMMIT_RUNNING`, calls filesystem data-submit hook, and wakes waiters.
- `journal_finish_inode_data_buffers()` waits for required inode data writeback and refiles inodes to the next transaction or clears dirty ranges.

Main commit function:
- `jbd2_journal_commit_transaction()` performs the complete transaction state machine:
  - Handles prior journal flush state.
  - Blocks overlapping fast commits and marks full commit ongoing.
  - Locks the running transaction, waits for outstanding updates, and releases unused reserved buffers.
  - Cleans checkpoint lists opportunistically.
  - Clears revoked flags and switches revoke tables.
  - Moves transaction from running to committing, records log start, and wakes waiters.
  - Submits ordered data buffers and writes revoke records.
  - Logs metadata through descriptor blocks and temporary shadow buffers, writing tags with block numbers, flags, UUID elision, and checksums.
  - Waits for metadata I/O, reclassifies shadowed buffers onto forget lists, then waits for descriptor/revoke control buffers.
  - Flushes filesystem device when needed before journal commit for external journals or tail updates.
  - Writes and waits for the commit record, with async-commit support.
  - Updates log tail when enough space is freed.
  - Processes the forget list: frees frozen/committed copies, removes old checkpoints, handles freed buffers, inserts new checkpoint records for dirty metadata, refiles/unfiles buffers, and may free truncated pages.
  - Adds the committed transaction to the checkpoint transaction ring.
  - Records run statistics, updates commit sequence and average commit time, invokes commit and fast-commit cleanup callbacks.
  - Marks transaction `T_FINISHED`, drops it immediately if no checkpoint buffers remain, wakes commit waiters, and accumulates history stats.

Important transaction states:
- `T_RUNNING`
- `T_LOCKED`
- `T_SWITCH`
- `T_FLUSH`
- `T_COMMIT`
- `T_COMMIT_DFLUSH`
- `T_COMMIT_JFLUSH`
- `T_COMMIT_CALLBACK`
- `T_FINISHED`

This file is the core durability path for JBD2: it orders data, metadata journal records, revoke records, cache flushes, commit blocks, checkpoint enrollment, callback execution, and transaction retirement.
