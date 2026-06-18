# sources/storage-engines/tikv/components/engine_traits/src/checkpoint.rs

Purpose: Abstracts engine checkpoint creation and database merge behavior.

Important APIs and control flow: `Checkpointable` associates a `Checkpointer`, creates one with `new_checkpointer`, and defines `merge` for combining DBs. `Checkpointer::create_at` writes a checkpoint to an output directory with optional Titan output directory and log-size flush threshold.

State, persistence, and dependencies: Checkpoints persist engine files to new directories, potentially involving SST, MANIFEST, WAL, and Titan blob state.

Integration points, risks, and test signals: Used by backup, snapshot, tablet, and migration workflows. Risks include incomplete flush before checkpoint, encryption metadata mismatches, Titan path handling, and merge conflicts. Shared encrypted checkpoint tests reopen the checkpoint and verify data plus key-manager cleanup.
