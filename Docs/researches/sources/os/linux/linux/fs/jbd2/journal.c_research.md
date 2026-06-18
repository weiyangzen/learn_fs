# File Research: sources/os/linux/linux/fs/jbd2/journal.c

## Role

`journal.c` is the central JBD2 journal lifecycle and log-management implementation. It manages journal objects, the `kjournald2` commit thread, journal superblock loading/updating, commit scheduling, fast-commit buffer allocation, log-space tail accounting, feature negotiation, journal flushing/wiping/destruction, abort/error state, proc statistics, shrinker registration, slab/cache setup, and `journal_head` attachment to buffer heads.

## Main Responsibilities

- Starts and stops the per-journal kernel thread through `jbd2_journal_start_thread()`, `kjournald2()`, and `journal_kill_thread()`.
- Schedules, waits for, and forces commits through `jbd2_log_start_commit()`, `jbd2_journal_start_commit()`, `jbd2_log_wait_commit()`, `jbd2_journal_force_commit()`, and `jbd2_complete_transaction()`.
- Allocates log blocks and descriptor buffers through `jbd2_journal_next_log_block()` and `jbd2_journal_get_descriptor_buffer()`.
- Maps logical journal blocks to physical blocks via `jbd2_journal_bmap()`, supporting external fixed journals and inode-backed journals.
- Writes journal metadata buffers with magic-number escaping and frozen-data handling in `jbd2_journal_write_metadata_buffer()`.
- Loads, validates, and updates the on-disk journal superblock.
- Initializes and destroys `journal_t` instances through `jbd2_journal_init_dev()`, `jbd2_journal_init_inode()`, `jbd2_journal_load()`, and `jbd2_journal_destroy()`.

## Commit Thread and Commit Control

`kjournald2()` loops until `JBD2_UNMOUNT`, waking for explicit commit requests, commit timer expiry, freezer events, or journal shutdown. It calls `jbd2_journal_commit_transaction()` when `j_commit_request` advances beyond `j_commit_sequence`.

The thread uses:
- `j_state_lock` for commit state.
- `j_wait_commit` for commit requests/timer wakeups.
- `j_wait_done_commit` to notify waiters when commit state changes or the thread exits.
- `j_commit_timer` to wake after the running transaction’s expiry time.

`jbd2_trans_will_send_data_barrier()` lets ordered-data callers determine whether a commit will issue the needed flush/barrier, avoiding duplicate barriers when possible.

## Fast Commit Support

The file implements the JBD2-side fast commit coordination:
- `jbd2_fc_begin_commit()` serializes fast commits against full commits and existing fast commits.
- `jbd2_fc_end_commit()` clears fast-commit state and wakes waiters.
- `jbd2_fc_end_commit_fallback()` converts a failed fast commit into a full commit request.
- `jbd2_fc_get_buf()`, `jbd2_fc_wait_bufs()`, and `jbd2_fc_release_bufs()` allocate and manage fast-commit write buffers in the fast-commit journal area.

Fast commits are disabled after recovery in `journal_reset()` until the filesystem explicitly enables them again.

## Superblock and Feature Handling

`journal_load_superblock()` reads the journal superblock, validates magic, block size, format, length, start block, feature flags, checksum compatibility, checksum type, and fast-commit sizing. It initializes tail/head fields and checksum seed.

Feature APIs include:
- `jbd2_journal_check_used_features()`
- `jbd2_journal_check_available_features()`
- `jbd2_journal_set_features()`
- `jbd2_journal_clear_features()`

`jbd2_journal_set_features()` upgrades checksum-v2 requests to checksum-v3, avoids enabling checksum-v1 together with v3, initializes fast-commit layout when requested, and refreshes transaction limits.

## Flush, Wipe, Erase, and Abort Paths

`jbd2_journal_flush()` forces the running/committing transaction to finish, checkpoints all checkpoint transactions, cleans the journal tail, marks the journal empty, and optionally discards or zeroes journal blocks via `__jbd2_journal_erase()`.

`jbd2_journal_wipe()` is a pre-load operation that either ignores or clears recoverable log contents.

`jbd2_journal_abort()` records a permanent in-memory abort state, stores an errno in the journal superblock, and starts the current transaction so journaled buffers can be released. `-ESHUTDOWN` has precedence over other abort errnos because it does not imply the same fsck requirement.

## Memory, Buffer, and Inode Integration

The file creates module-global caches for revoke records/tables, journal heads, handles, JBD2 inodes, transactions, and power-of-two data-copy slabs.

`jbd2_journal_add_journal_head()`, `jbd2_journal_grab_journal_head()`, and `jbd2_journal_put_journal_head()` attach, refcount, detach, and free `journal_head` objects associated with `buffer_head`s. A buffer with `BH_JBD` gets an elevated buffer refcount and remains protected from normal buffer release until the journal head reference count reaches zero.

`jbd2_journal_init_jbd_inode()` and `jbd2_journal_release_jbd_inode()` integrate VFS inodes with ordered-data tracking, waiting for commit writeout before removing inodes from transaction lists.

## Important Invariants

- Commit state updates are protected by `j_state_lock`; transaction buffer lists by `j_list_lock`; checkpoint tail updates by `j_checkpoint_mutex`.
- Journal superblock tail updates use FUA when journal space can be reused after the update.
- `jbd2_journal_load()` starts from an abort-marked journal and clears `JBD2_ABORT` only after successful recovery.
- A clean journal is represented on disk by `s_start == 0`.
- `journal_head` removal requires no active running, next, checkpoint transaction, or transaction list membership.
- Log transaction limits must be recomputed after journal size, checksum tag format, fast-commit area, or feature changes.

## Research Notes

This file is the glue between the JBD2 transaction engine, recovery/checkpoint logic, block-device write ordering, and filesystem users such as ext4. Most correctness risks are around ordering: log-tail durability before reuse, superblock writes with barriers, buffer copy-out during commit, and consistent journal abort propagation.
