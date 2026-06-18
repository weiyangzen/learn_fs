# sources/sync-backup/kopia/snapshot/upload/checkpoint_registry.go

Purpose: tracks active upload checkpoint callbacks and materializes checkpointed directory entries into a directory manifest builder.

Important APIs/types/functions: `checkpointFunc`, `checkpointRegistry`, `addCheckpointCallback`, `removeCheckpointCallback`, and `runCheckpoints`.

Control flow: callbacks are stored by entry name under a mutex. `runCheckpoints` invokes each callback, skips nil results, randomizes names for non-directory checkpoint entries using `.checkpointed.<name>.<uuid>`, and adds entries to a `snapshotfs.DirManifestBuilder`.

State and persistence: registry state is in-memory. Checkpoint results may later be persisted when the builder's manifest is written by the upload path. Randomized file names intentionally prevent checkpoint objects from becoming authoritative normal entries in later runs.

Dependencies and integration points: used by the snapshot uploader during long directory uploads and checkpoint creation.

Risks and test signals: callback map iteration order is nondeterministic, but final builder sorting provides stable manifest order. Callback errors abort the checkpoint run. Tests verify removal, nil skip, directory name preservation, and file name randomization prefix.
