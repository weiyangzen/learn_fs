<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister.go

This file implements the legacy whole-metadata `robustness.Persister` on top of Kopia snapshots. `KopiaPersister` embeds `Simple`, owns local metadata and persistence dirs, and reuses `kopiaConnector`.

`NewPersister` creates temp dirs, initializes the connector, and overrides server init hooks because this persister does not support server mode. `LoadMetadata` lists snapshots, restores the latest into the persistence dir, opens `metadata-store-latest`, and JSON-decodes it into `Simple`. `FlushMetadata` JSON-encodes `Simple` into that file and snapshots the persistence dir. Repo connection methods delegate to the connector/snapshotter.

State is both in-memory `Simple` metadata and the latest metadata snapshot in the metadata repository. Risks include relying on list order for latest snapshot, stale files in the persistence dir, temp file cleanup with ignored errors, and larger metadata snapshots than the key/value light persister. Tests are mostly legacy/integration; current harnesses prefer `KopiaPersisterLight`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister.go -->
