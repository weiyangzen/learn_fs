# sources/sync-backup/kopia/internal/repodiag/log_manager_test.go

Purpose: validates diagnostic log manager modes and flushing behavior.

Important APIs/types/functions: `TestLogManager_Enabled`, `TestLogManager_AutoFlush`, `TestLogManager_NotEnabled`, `TestLogManager_CancelledContext`, and `TestLogManager_Null`.

Control flow: constructs log managers with fake writers/storage, emits log entries, toggles enablement, syncs, and asserts blob/text outputs or absence of output.

State and persistence behavior: test state is in-memory buffers and storages.

Dependencies and integration points: exercises `contentlog` integration and `BlobWriter`-backed persistence.

Risks and test signals: useful for regression around flush thresholds and disabled logging; race detector helps for concurrent logging paths.
