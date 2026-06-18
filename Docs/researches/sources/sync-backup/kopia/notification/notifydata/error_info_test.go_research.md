<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/error_info_test.go -->
# sources/sync-backup/kopia/notification/notifydata/error_info_test.go

- Purpose: Tests `ErrorInfo` construction, timestamp helpers, duration, and event round trip.
- Important APIs/types/functions: `TestNewErrorInfo`.
- Control flow: Creates fixed start/end times and an error, checks all fields and truncated helper methods, then calls shared JSON/gRPC round trip.
- State and persistence: In-memory payload only.
- Dependencies and integration points: Uses `clock`, `testify/require`, and `notifydata`.
- Risks and edge cases: Uses a simple error, so wrapped stack/detail formatting is not covered.
- Test signals: Direct coverage for `error_info.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/error_info_test.go -->
