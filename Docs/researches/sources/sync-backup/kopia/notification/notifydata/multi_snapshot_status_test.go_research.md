<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/multi_snapshot_status_test.go -->
# sources/sync-backup/kopia/notification/notifydata/multi_snapshot_status_test.go

- Purpose: Tests snapshot notification metrics, deltas, statuses, and JSON round trips.
- Important APIs/types/functions: `TestOverallStatus`, `TestStatusCode`, `TestManifestWithErrorMethods`, `TestTotalSizeDelta`, `TestTotalFilesDelta`, `TestTotalDirsDelta`, `TestTotalFiles`, `TestTotalDirs`, `TestTotalSize`.
- Control flow: Table tests construct manifests with root summaries, previous manifests, incomplete reasons, and top-level errors, then assert status codes/text and derived numeric values.
- State and persistence: In-memory snapshot manifest payloads only.
- Dependencies and integration points: Uses `fs`, `clock`, `snapshot`, and `testify/require`.
- Risks and edge cases: Strong coverage of helper semantics; template rendering is tested separately.
- Test signals: Direct coverage for `multi_snapshot_status.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/multi_snapshot_status_test.go -->
