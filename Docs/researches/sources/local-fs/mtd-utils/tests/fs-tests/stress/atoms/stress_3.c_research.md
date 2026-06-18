# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/stress_3.c

## Purpose
Sparse-file hole creation and fill stress atom.

## Key Elements
Creates `stress_3_test_file_<pid>`, seeks to `tests_size_parameter`, writes one byte to create a hole, rewinds and fills the hole with random data, truncates the file to zero, closes it, and optionally deletes it.

## Dependencies
Uses POSIX file APIs and shared `tests.h`.

## Behavior/Risks
Stresses sparse-file allocation and truncate-after-fill behavior. `ftruncate(fd, 0)` tolerates `ENOSPC`, which is unusual but expected for the test environment.
