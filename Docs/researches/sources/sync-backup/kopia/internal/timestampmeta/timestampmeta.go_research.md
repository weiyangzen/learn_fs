<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/timestampmeta/timestampmeta.go -->
# sources/sync-backup/kopia/internal/timestampmeta/timestampmeta.go

- Purpose: Converts timestamps to/from metadata map values stored as Unix nanoseconds.
- Important APIs/types/functions: `ToMap`, `FromValue`.
- Control flow: `ToMap` returns nil for zero time, otherwise a one-entry map with decimal nanoseconds. `FromValue` parses an int64 and returns `time.Unix(0, nanos)` plus success flag.
- State and persistence: Metadata maps are caller-owned; no package state.
- Dependencies and integration points: Intended for per-blob metadata/tags; depends on `strconv` and `time`.
- Risks and edge cases: Invalid numeric strings fail gracefully; timezone names are not preserved because Unix nanoseconds are absolute.
- Test signals: `timestampmeta_test.go` covers `ToMap`; `FromValue` lacks direct test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/timestampmeta/timestampmeta.go -->
