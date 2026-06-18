<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/simple_test.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/simple_test.go

This file tests `Simple` metadata storage. It validates storing and loading byte values, deleting keys, missing-key behavior, and index helper interaction.

The test is a direct signal for the legacy persister's in-memory state before JSON flush and restore. It depends on `testify/require` and robustness error sentinels.

Residual risks include concurrent access, JSON round trips through `KopiaPersister`, and mutation of returned byte slices. The test nevertheless protects the basic contract used by engine metadata save/load.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/simple_test.go -->
