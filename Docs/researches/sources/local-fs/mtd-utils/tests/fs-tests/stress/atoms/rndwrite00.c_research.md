# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rndwrite00.c

## Purpose
Random overwrite stress test for a single large file with in-memory verification.

## Key Elements
Creates `rndwrite00_test_file_<pid>`, fills an in-memory buffer and file with random data, performs repeated random writes up to 4095 bytes without changing file size, mirrors writes in memory, periodically verifies file contents, and optionally deletes the file.

## Dependencies
Uses POSIX file APIs and shared random/argument helpers.

## Behavior/Risks
Allocates `tests_size_parameter` bytes of memory, so large `-z` values can exhaust RAM. The `check_every = actual_size / 8192` calculation can become zero for small actual files, causing modulo-by-zero if the loop proceeds.
