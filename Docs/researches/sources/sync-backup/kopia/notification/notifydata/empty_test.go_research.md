<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/empty_test.go -->
# sources/sync-backup/kopia/notification/notifydata/empty_test.go

- Purpose: Tests empty notification payload JSON/gRPC type round trip.
- Important APIs/types/functions: `TestEmptyEventInfo`.
- Control flow: Delegates to shared `testRoundTrip` with `EmptyEventData`.
- State and persistence: In-memory JSON only.
- Dependencies and integration points: Uses external `notifydata_test` package.
- Risks and edge cases: Minimal payload test only.
- Test signals: Direct coverage for `empty.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/empty_test.go -->
