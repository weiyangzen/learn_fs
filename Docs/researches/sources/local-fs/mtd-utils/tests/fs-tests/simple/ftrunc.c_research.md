# File Research: sources/local-fs/mtd-utils/tests/fs-tests/simple/ftrunc.c

## Purpose
Simple truncate test for a large file.

## Key Elements
Creates `ftrunc_test_file`, writes up to `tests_size_parameter` bytes of PID-seeded random data, truncates the file by one byte if nonempty, closes it, and unlinks it.

## Dependencies
Uses POSIX open/write/ftruncate/unlink and shared `tests.h`.

## Behavior/Risks
Treats `ENOSPC` during writing as expected. It does not verify final contents; it only verifies syscall success through `CHECK()`.
