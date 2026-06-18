# sources/storage-engines/tikv/src/storage/txn/commands/flashback_to_version.rs

## Purpose
Executes the write half of flashback-to-version. It applies state-specific MVCC mutations after the read phase has found locks or keys requiring rollback, prewrite, flashback write, or commit.

## Important APIs, Types, and Functions
`FlashbackToVersion` stores `start_ts`, `commit_ts`, target `version`, range bounds, and `FlashbackToVersionState`. It calls `rollback_locks`, `prewrite_flashback_key`, `flashback_to_version_write`, and `commit_flashback_key` from `actions::flashback_to_version`. It customizes metrics tags based on state.

## Control Flow
`process_write` creates an `MvccReader` with flashback allowed and an `MvccTxn` at zero. For `RollbackLock`, it rolls back a batch and updates `next_lock_key` if more remain. `Prewrite` writes the sentinel first-user-key lock. `FlashbackWrite` rewrites historical versions for a batch and advances `next_write_key`. `Commit` commits the sentinel key. For batch states, it returns a `NextCommand` back to `FlashbackToVersionReadPhase`; for prewrite/commit, it returns `Res`.

## State and Persistence
Writes are marked `allowed_in_flashback`. `FlashbackWrite` additionally marks `one_pc` so CDC treats the rewrite as a 1PC transaction. Latches are derived from the concrete keys in the current state. No released locks or known transaction status are emitted.

## Dependencies and Integration Points
Pairs tightly with `flashback_to_version_read_phase.rs`; the read phase chooses the next state and keys, this file persists them. It integrates with MVCC flashback-specific reader permissions and scheduler `NextCommand` chaining.

## Risks and Test Signals
Risks include batch continuation keys, sentinel key consistency between prewrite and commit, CDC metadata correctness, and allowing writes inside flashback mode only. Failpoints cover failure after the first flashback batch; broader flashback action tests validate data restoration behavior.
