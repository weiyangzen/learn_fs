<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/failing_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/failing_test.py

Purpose: tests the synthetic `ChunkerFailing` used to simulate read/chunk failures.

Important APIs: `ChunkerFailing`, `BytesIO`, `pytest.raises`, and `CH_DATA`.

Control flow: creates data larger than two fixed-size blocks and a failing chunker configured as `rEErrr`. The first generator yields block 0 then raises on block 1; the second new generator raises again; the third generator succeeds for subsequent blocks. Assertions check data slices and allocation metadata.

State and persistence: no files; failure state is maintained by the chunker instance across `chunkify` calls.

Dependencies/integration: useful for testing retry/error paths elsewhere. Risks include stateful failure counters being surprising across generator instances. Test signals are raised `OSError` and exact recovered chunks.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/failing_test.py -->
