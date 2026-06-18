<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/faketimeserver.go -->
# sources/sync-backup/kopia/tests/testenv/faketimeserver.go

This file implements a small HTTP handler that returns fake time information as JSON. `FakeTimeServer` wraps a `Now` function; `ServeHTTP` encodes the current fake time and a two-second validity duration.

The integration point is tests that need Kopia instances to synchronize to controllable time signals. `NewFakeTimeServer` constructs the handler, and the type satisfies `http.Handler`.

State is delegated to the provided `Now` callback. Risks include ignored JSON encode errors, no method/path validation, and tests needing to keep the callback concurrency-safe. Test signals come from time-dependent integration tests outside this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/faketimeserver.go -->
