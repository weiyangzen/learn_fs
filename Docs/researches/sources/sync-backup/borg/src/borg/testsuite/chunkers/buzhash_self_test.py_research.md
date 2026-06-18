<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash_self_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash_self_test.py

Purpose: Borg self-test coverage for the classic 32-bit buzhash chunker.

Important APIs: `Chunker`, `buzhash`, `buzhash_update`, `get_chunker`, `BaseTestCase`, `cf`, and `CHUNKER_PARAMS`.

Control flow: `test_chunkify` verifies exact chunk boundaries for empty, large, and repeated strings across seeds and chunker parameters. `test_buzhash` checks known hash outputs, rolling update equivalence, and barrel-shift behavior beyond 31 bytes. `test_small_reads` verifies chunking remains correct for a file-like object that returns one byte at a time.

State and persistence: no persistent state; all data is in `BytesIO`.

Dependencies/integration: self-test module must avoid pytest and match `borg.selftest` expected method count. Risks are repository deduplication compatibility if chunk boundaries change and subtle small-read buffer bugs. Test signals are exact chunk arrays, known hash integers, and reconstructed content.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash_self_test.py -->
