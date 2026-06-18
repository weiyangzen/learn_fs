<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/timestampmeta/timestampmeta_test.go -->
# sources/sync-backup/kopia/internal/timestampmeta/timestampmeta_test.go

- Purpose: Tests timestamp-to-map conversion.
- Important APIs/types/functions: `timeValue`, `storedValue`, `TestToMap`.
- Control flow: Compares a fixed UTC time to the expected nanosecond string and verifies zero time returns nil.
- State and persistence: None beyond table globals.
- Dependencies and integration points: Uses external test package `timestampmeta_test` and `testify/require`.
- Risks and edge cases: Does not test `FromValue` or malformed metadata.
- Test signals: Partial direct coverage for `timestampmeta.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/timestampmeta/timestampmeta_test.go -->
