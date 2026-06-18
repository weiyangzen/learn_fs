# sources/sync-backup/kopia/snapshot/upload/checkpoint_registry_test.go

Purpose: unit coverage for upload checkpoint registration, removal, nil checkpoints, and generated entry names.

Important APIs/types/functions: `TestCheckpointRegistry`, `checkpointRegistry`, `snapshotfs.DirManifestBuilder`, and mock filesystem entries.

Control flow: the test registers callbacks for a directory and several files, removes one duplicate-name callback twice, seeds the builder with a pre-existing entry, runs checkpoints, builds a manifest, and inspects sorted entry names.

State and persistence: all state is in memory. UUID suffixes are only checked by prefix because they are random.

Dependencies and integration points: validates checkpoint output shape consumed by uploader directory manifests.

Risks and test signals: duplicate entry names in the registry overwrite earlier callbacks before removal. Expected order relies on `DirManifestBuilder.Build` sorting directories before non-directories by name. The test does not cover callback errors.
