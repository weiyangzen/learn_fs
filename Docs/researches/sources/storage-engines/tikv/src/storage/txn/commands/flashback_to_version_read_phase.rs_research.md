# sources/storage-engines/tikv/src/storage/txn/commands/flashback_to_version_read_phase.rs

## Purpose
Implements the read half and state machine driver for flashback-to-version. It scans locks and write records in bounded batches, then emits write commands that perform each phase.

## Important APIs, Types, and Functions
`FlashbackToVersionState` has `RollbackLock`, `Prewrite`, `FlashbackWrite`, and `Commit` variants. `new_flashback_rollback_lock_cmd` builds prepare-phase commands; `new_flashback_write_cmd` builds finish-phase commands. `process_read` calls `flashback_to_version_read_lock`, `flashback_to_version_read_write`, `get_first_user_key`, and `check_flashback_commit`.

## Control Flow
The full flow is documented as four phases: rollback existing locks, prewrite the first user key to hold resolved-ts, rewrite latest changed keys back to `version`, then commit the sentinel key. The reader runs forward with flashback allowed and a write-CF minimum timestamp hint excluding versions at or below the target. Empty rollback-lock batches transition to prewrite or finish if no user key exists. Flashback-write batches skip the sentinel key until final commit and return directly if a retry already committed it.

## State and Persistence
The read phase is readonly and has an empty latch. It returns `ProcessResult::NextCommand` with `Command::FlashbackToVersion` when writes are needed, or `Res` when no work remains. It only collects read statistics and key-read histograms.

## Dependencies and Integration Points
Depends on MVCC forward scans, flashback action helpers, scheduler command chaining, and command metrics split between read-lock and read-write states. It is constructed from prepare and finish flashback RPCs in `mod.rs`.

## Risks and Test Signals
Risks include infinite loops when a batch has a single key, invalid `commit_ts <= start_ts`, retry idempotence, and correct range-bound handling when `start_key` is not a real user key. Inline comments explicitly guard the single-key next-key case and sentinel-key retry behavior.
