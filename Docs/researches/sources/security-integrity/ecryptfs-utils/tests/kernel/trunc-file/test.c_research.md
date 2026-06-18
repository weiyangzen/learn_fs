## sources/security-integrity/ecryptfs-utils/tests/kernel/trunc-file/test.c

Purpose: C data-integrity test for repeated file shrink and re-expand operations. It writes deterministic pseudo-random data, repeatedly truncates to half sizes, validates retained data and file size, expands back to full size, and verifies the new tail is zero-filled.

Important APIs and functions: `write_buff`, `read_buff`, `test_write_random`, `test_read_random`, `test_read_rest`, `test_exercise`, `sighandler`, `main`, plus `open`, `write`, `read`, `lseek`, `ftruncate`, `fstat`, `close`, `unlink`. Control flow seeds `random()` with a fixed value for repeatable content, performs full write/read sanity, loops `trunc_size >>= 1`, and validates both content preservation and hole/zero semantics after each extension.

State and persistence: Mutates one test file and removes it at the end. Dependencies are filesystem truncation semantics and eCryptfs block translation. Integration is via `trunc-file.sh`. Risks include a missing explicit return in `test_write_random` on success, though callers only test `< 0`; also heavy IO scales with selected size. Test signal is strong because it checks data bytes, size metadata, zero-fill behavior, and cleanup.
