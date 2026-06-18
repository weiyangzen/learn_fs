<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/index_test.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/index_test.go

This file unit-tests the `Index` helper. `TestIndex` validates adding keys to indexes, checking membership, retrieving keys, and removing entries.

The test provides direct signals for the in-memory index set semantics used by snapshot metadata stores. It depends on `testify/require` and does not involve filesystem or Kopia state.

Residual risks not covered include concurrent access, JSON round-trip behavior when embedded in larger metadata, nil receiver/map initialization behavior, and deterministic ordering. The test is still a useful narrow guard for basic index correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/index_test.go -->
