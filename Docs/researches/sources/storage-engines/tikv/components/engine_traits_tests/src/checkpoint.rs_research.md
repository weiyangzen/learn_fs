# sources/storage-engines/tikv/components/engine_traits_tests/src/checkpoint.rs

Purpose: Tests encrypted checkpoint creation and cleanup through the generic checkpoint traits.

Important APIs and control flow: The test creates a file-security config and key manager, opens an encrypted engine with all CFs, writes and syncs a key, creates a checkpoint at another path, reopens the checkpoint with the same encrypted options, verifies the key, drops engines, trashes both directories through encryption-aware cleanup, and expects the key manager file count to return to zero.

State, persistence, and dependencies: State includes encrypted DB files, checkpoint files, key-manager metadata, and temporary directories.

Integration points, risks, and test signals: Covers `Checkpointable`, `Checkpointer`, encryption metadata linking, checkpoint reopenability, and cleanup. Risks caught include missing encrypted file links, incomplete checkpoint state, and leaked key metadata.
