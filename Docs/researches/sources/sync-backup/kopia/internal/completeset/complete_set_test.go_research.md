# sources/sync-backup/kopia/internal/completeset/complete_set_test.go

Purpose: table-driven coverage for complete-set detection and filtering.

Important APIs/types/functions: `TestFindFirstAndAll`, `idsFromMetadataSets`, and `dummyMetadataForIDs`.

Control flow: each case builds metadata from blob IDs, calls `FindFirst`, `FindAll`, and `ExcludeIncomplete`, converts results back to IDs, and compares expected ordering.

State and persistence behavior: in-memory only. The tests encode the important ordering rule that the first complete set is whichever set becomes complete earliest in input order, with malformed IDs treated as singleton sets.

Dependencies/integration: uses `completeset`, `blob`, and `testify/require`.

Risks/test signals: tests do not cover duplicate members in the same set or names with extra dash-separated parts before `s`/`c`. The existing cases are strong regression signals for epoch compaction set discovery.
