<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/metadata.go -->
# sources/sync-backup/kopia/tests/robustness/engine/metadata.go

This file persists and restores engine metadata keys for action history, cumulative stats, and the snapshot ID index. The public surface is engine methods `saveLog`, `loadLog`, `saveStats`, `loadStats`, `saveSnapIDIndex`, and `loadSnapIDIndex`; each marshals or unmarshals JSON against `e.MetaStore`, which satisfies the robustness persister/store contract.

Control flow is uniform: save methods `json.Marshal` current engine state and call `Store`; load methods call `Load`, tolerate `robustness.ErrKeyNotFound` as an empty initial state, and decode JSON into engine fields. `loadLog` additionally sets `ThisRunStartIdx` to the pre-existing log length so later diagnostics can isolate the current run.

Persistence behavior depends on stable JSON encodings of `Log`, `Stats`, and `Checker.SnapIDIndex`. Integration points are `snapmeta.KopiaPersisterLight`, legacy `KopiaPersister`, and engine shutdown/init. Risks include corrupt JSON preventing startup, schema drift across test binary versions, and silent first-run behavior when metadata is missing. Test signals come from robustness tests that resume prior state and from snapmeta persister tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/metadata.go -->
