# sources/storage-engines/pebble/internal/bytesprofile/bytesprofile_test.go

Purpose: Tests byte profile aggregation and formatting.

APIs and types: Exercises `NewProfile`, `Record`, `String`, and `Collect`.

Control flow and state: Records two distinct call stacks with known byte totals and counts, checks formatted output contains expected humanized counts/bytes, then checks structured stats ordering.

Persistence and dependencies: No persistence. Uses testify require.

Integration points: Protects diagnostic reporting used by internal profiling tools.

Risks: Stack identity relies on call sites remaining distinct; refactors can require expectation updates.

Test signals: Good focused coverage for aggregation and descending-byte ordering.
