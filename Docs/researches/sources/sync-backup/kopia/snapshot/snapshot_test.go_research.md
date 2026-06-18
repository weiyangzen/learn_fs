# sources/sync-backup/kopia/snapshot/snapshot_test.go

Purpose: black-box tests for the snapshot package public API around manifest storage, source parsing, pins, and time sorting.

Important APIs/types/functions: `TestSnapshotsAPI`, `verifySnapshotManifestIDs`, `mustSaveSnapshot`, `verifySources`, `verifyListSnapshots`, `verifyLoadSnapshots`, `TestParseSourceInfo`, `TestParseInvalidSourceInfo`, `TestUpdatePins`, `TestSortByTimeAscending`, and `TestSortByTimeDescending`.

Control flow: tests create an in-memory repo environment, save manifests for two sources, list/filter/load them, update pins and verify a new manifest ID, parse source strings, and assert sort ordering with same start times but different end times.

State and persistence: writes snapshot manifests to the test repository and updates one manifest's pins. Source parsing uses the current working directory for bare paths.

Dependencies and integration points: covers repository manifest APIs, `snapshot.SourceInfo`, `manifest.ID`, and `repotesting`.

Risks and test signals: expected values rely on local absolute path normalization. Signals are exact manifest lists, source lists, pin sorting/deduplication, parse errors for invalid host syntax, and sort monotonicity.
