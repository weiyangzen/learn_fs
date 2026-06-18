<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_bloom.py -->
# sources/sync-backup/bup/test/int/test_bloom.py

Purpose: tests the Python bloom filter reader/writer implementation. Important APIs are `BloomWriter`, `BloomReader`, a local dataclass fixture, and pytest tmpdir. Control flow writes bloom filters containing object IDs, reopens them, verifies membership and non-membership behavior, checks error handling for missing/corrupt files, and runs a larger bloom population path. State is the temporary bloom file and in-memory object IDs. Dependencies include `bup.bloom`, Python file IO, errno constants, and pytest. Risks are probabilistic false positives, file format compatibility, large-filter memory cost, and platform-specific error codes. Test signals are membership assertions, expected exceptions, and successful large bloom read/write.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/test_bloom.py -->
