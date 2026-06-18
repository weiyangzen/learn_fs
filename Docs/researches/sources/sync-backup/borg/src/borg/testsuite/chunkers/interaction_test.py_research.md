<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/interaction_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/interaction_test.py

Purpose: integration-style tests for reader/chunker buffer interaction across fixed, buzhash, and buzhash64 chunkers.

Important APIs: `get_chunker`, chunker parameter constants (`CH_FIXED`, `CH_BUZHASH`, `CH_BUZHASH64`), allocation constants, and `BytesIO`.

Control flow: parametrized chunker settings generate a large byte stream containing random data, zeros, and random data. The test chunks it, counts `CH_DATA`, `CH_ALLOC`, and `CH_HOLE`, asserts data and allocated-zero chunks are present and holes are absent for `BytesIO`, then reassembles chunks by expanding non-data allocation to zeros and compares against original data.

State and persistence: in-memory only.

Dependencies/integration: checks boundary handling between reader block size and chunker block size, especially awkward fixed sizes. Risks include buffer slicing bugs, misclassified zero ranges, and absent allocation metadata. Test signals are allocation counts, reconstructed size, and exact byte equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/interaction_test.py -->
