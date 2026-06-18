<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash_test.py

Purpose: pytest tests for classic buzhash chunker stability, chunk-size distribution, and slow fuzz reconstruction.

Important APIs: `Chunker`, `cf`, `cf_expand`, `hex_to_bin`, `CHUNKER_PARAMS`, `HASH_WINDOW_SIZE`, and helper `H`.

Control flow: deterministic `twist` data is chunked across window/min/max/mask/seed combinations, then a golden digest asserts chunkpoint compatibility. Distribution test chunks 1 MiB random data and checks number of chunks, min/max clipping, and low min/max clipping counts. Slow fuzz iterates random signed 32-bit seeds and sizes over random, repeated nonzero, and zero data, reconstructing output.

State and persistence: in-memory only; slow test gated by `BORG_TESTS_SLOW`.

Dependencies/integration: depends on default chunker parameters being `CH_BUZHASH` and algorithmic compatibility. Risks include statistical distribution failures, golden hash changes, and CPU-heavy fuzz. Test signals are golden digest, chunk size bounds, and reconstructed byte equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash_test.py -->
