# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/stress_2.c

## Purpose
Repeated write stress on an open deleted file.

## Key Elements
Creates `stress_2_test_file`, immediately unlinks it while holding the descriptor, then repeatedly rewinds and writes `tests_size_parameter` bytes of fresh random data until repeat count expires.

## Dependencies
Uses POSIX file APIs and shared `tests.h`.

## Behavior/Risks
Exercises orphaned inode data writes. The file is invisible after unlink and is reclaimed only when the descriptor closes.
