<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/persister.go -->
# sources/sync-backup/kopia/tests/robustness/persister.go

This file defines persistence contracts for robustness metadata. `Store` provides key/value `Store`, `Load`, and `Delete` methods. `Persister` embeds `Store` and adds repository lifecycle methods `LoadMetadata`, `FlushMetadata`, `GetPersistDir`, and `Cleanup`.

The engine uses the key/value operations for log, stats, and snapshot index metadata. Legacy implementations also use load/flush lifecycle methods to snapshot a whole metadata file; the lightweight persister makes those lifecycle hooks no-ops because it stores each key as a Kopia snapshot.

There is no internal state here. Risks are contract ambiguity between key/value persistence and whole-metadata persistence; implementations must define `ErrKeyNotFound` semantics consistently. Test signals are snapmeta persister tests and robustness engine init/shutdown behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/persister.go -->
