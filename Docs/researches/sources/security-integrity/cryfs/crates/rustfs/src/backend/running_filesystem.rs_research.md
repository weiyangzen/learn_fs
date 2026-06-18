# sources/security-integrity/cryfs/crates/rustfs/src/backend/running_filesystem.rs

Purpose: wraps a mounted FUSE background session in an RAII object that can unmount explicitly, on process exit signals, on a cancellation trigger, or during drop. It abstracts over both supported backend session types via `BackgroundSession`.

Important APIs: `BackgroundSession::join` and `is_finished`; `RunningFilesystem::new`, `unmount_join`, `unmount_on_trigger`, `block_until_unmounted`, and `Drop`. Feature-gated impls adapt `fuser_fusemt::BackgroundSession` and `fuser::BackgroundSession`; the latter uses `umount_and_join`.

Control flow and state: the session is stored as `Arc<Mutex<Option<BS>>>`. Every unmount path takes the option, making unmount idempotent and preventing double joins. `AtExitHandler` owns a closure that joins during SIGTERM/SIGINT/SIGQUIT handling. `unmount_on_trigger` spawns a Tokio task waiting on `CancellationToken`. `block_until_unmounted` polls `is_finished` every 100 ms.

Dependencies and integration: used by backend mount/spawn paths and tests. It depends on `cryfs_utils::at_exit`, `tokio_util`, logging, and fuser session APIs.

Risks and tests: busy polling is noted as a TODO. Drop logs unmount errors instead of panicking, while tests use explicit `unmount_join` to fail loudly. The mutex unwraps assume no poisoning.
