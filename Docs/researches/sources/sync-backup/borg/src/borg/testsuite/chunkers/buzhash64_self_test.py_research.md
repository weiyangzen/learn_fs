<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash64_self_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash64_self_test.py

Purpose: Borg self-test coverage for 64-bit buzhash chunker behavior without importing pytest.

Important APIs: `ChunkerBuzHash64`, `buzhash64`, `buzhash64_update`, `get_chunker`, `BaseTestCase`, `cf`, fixed test keys `key0`/`key1`/`key2`, and `CHUNKER64_PARAMS`.

Control flow: `test_chunkify64` feeds byte streams into the chunker with different keys and parameters and asserts exact chunk boundaries and full reconstruction. `test_buzhash64` checks known hash values, rolling update equivalence, and barrel-shift behavior beyond 63 bytes. `test_small_reads64` defines a file-like object returning one byte per read and verifies the default chunker reconstructs the expected data.

State and persistence: no persistent state; all tests use `BytesIO` and deterministic keys.

Dependencies/integration: part of Borg's self-test count, so it avoids pytest constructs. Risks include any chunk-boundary change bloating existing repositories and self-test count drift when methods change. Test signals are `BaseTestCase.assert_equal` exact values and reconstructed bytes.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash64_self_test.py -->
