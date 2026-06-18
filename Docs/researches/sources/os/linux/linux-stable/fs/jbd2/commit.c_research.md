# File Research: sources/os/linux/linux-stable/fs/jbd2/commit.c

Implements the full JBD2 transaction commit state machine.

Major phases in `jbd2_journal_commit_transaction()`:
- Blocks fast commits and locks the running transaction.
- Waits for outstanding updates, releases unused reserved buffers, cleans checkpoint lists, clears revoke flags, and switches revoke tables.
- Moves the transaction through `T_LOCKED`, `T_SWITCH`, `T_FLUSH`, `T_COMMIT`, `T_COMMIT_DFLUSH`, `T_COMMIT_JFLUSH`, `T_COMMIT_CALLBACK`, and finally `T_FINISHED`.
- Submits ordered data buffers before metadata when required.
- Writes revoke records, descriptor blocks, metadata shadow buffers, checksums, and commit records.
- Waits for metadata and control-buffer I/O, aborting the journal on failures.
- Flushes filesystem or journal devices when barrier and external journal rules require it.
- Updates the journal tail when enough checkpointed space can be freed.
- Processes the forget list, frees frozen/committed copies, handles freed buffers, re-checkpoints dirty buffers, and releases or refiles journal heads.
- Adds the committed transaction to the checkpoint list, runs callbacks, updates commit sequence/timing/statistics, wakes waiters, and drops the transaction if no checkpointing remains.

Supporting functions:
- `journal_end_buffer_io_sync()` handles journal buffer I/O completion and wakes shadowed metadata buffers.
- `release_buffer_page()` tries to strip buffers from truncated detached pages.
- `journal_submit_commit_record()` writes the commit block, including timestamps, checksum fields, and barrier/FUA flags.
- `journal_wait_on_commit_record()` waits for the commit block and detects I/O failure.
- `jbd2_submit_inode_data()` and `jbd2_wait_inode_data()` expose inode data submission/wait helpers.
- `journal_submit_data_buffers()` and `journal_finish_inode_data_buffers()` walk the transaction inode list with `JI_COMMIT_RUNNING` protection.
- `jbd2_checksum_data()`, `write_tag_block()`, and `jbd2_block_tag_csum_set()` implement metadata/tag checksum support.

Important invariants:
- Metadata buffers are written through temporary shadow buffers so original buffers can be protected while journal I/O is in flight.
- Descriptor tags record target block numbers, escape flags, UUID elision, and checksums.
- Async commit writes the commit record before waiting for all earlier log I/O, then flushes appropriately.
- Forget-list processing must tolerate concurrent additions from unmap paths, so it loops with `j_list_lock`.
- `j_list_lock` and `j_state_lock` together protect the transition to `T_FINISHED` against checkpoint races.
