# File Research: sources/local-fs/mtd-utils/tests/fs-tests/simple/perf.c

## Purpose
Measures write, unmount, mount, and read timing for a test file.

## Key Elements
Writes a PID-seeded file of `tests_size_parameter` bytes, fsyncs and closes it, unmounts and remounts the test filesystem, reads the file back in 32 KiB blocks, deletes it, and prints timing plus KiB/s rates.

## Dependencies
Uses shared mount helpers from `tests.h`, POSIX timing and file APIs.

## Behavior/Risks
Unmounts/remounts the test filesystem and assumes enough privilege. `speed()` divides by elapsed microseconds, so extremely fast operations could risk divide-by-zero.
