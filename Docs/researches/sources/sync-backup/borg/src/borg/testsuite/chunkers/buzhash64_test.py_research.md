<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash64_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash64_test.py

Purpose: pytest regression/fuzz tests for 64-bit buzhash chunker stability, size distribution, keyed table generation, and reconstruction.

Important APIs: `ChunkerBuzHash64`, `buzhash64_get_table`, `cf`, `cf_expand`, `hex_to_bin`, `CHUNKER64_PARAMS`, and local digest helper `H`.

Control flow: `test_chunkpoints64_unchanged` runs many parameter/key combinations over deterministic pseudo-random data and hashes chunk digests to assert a golden overall hash. Distribution test chunks 1 MiB random data and checks counts and min/max clipping. Table test asserts 256 integer entries, deterministic per key, different across keys, and exactly half of entries set for each bit. Slow fuzz reconstructs random, repeated nonzero, and zero data for many keys/sizes.

State and persistence: in-memory only, gated slow fuzz by `BORG_TESTS_SLOW`.

Dependencies/integration: depends on chunker algorithm stability and keyed table balance. Risks include golden hash churn from performance changes, randomness making distribution tests statistically sensitive, and CPU-heavy fuzz. Test signals are golden digest, range/count assertions, table bit counts, and reconstructed content equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/buzhash64_test.py -->
