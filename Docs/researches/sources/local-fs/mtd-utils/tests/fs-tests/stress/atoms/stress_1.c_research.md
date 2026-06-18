# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/stress_1.c

## Purpose
Simple large-file creation/overwrite stress atom.

## Key Elements
Creates `stress_1_test_file_<pid>`, writes up to `tests_size_parameter` bytes of PID-seeded random data, closes it, and deletes it when `-e` is set.

## Dependencies
Uses POSIX file APIs and shared `tests.h`.

## Behavior/Risks
Treats `ENOSPC` during writing as expected and leaves the file behind unless delete option is set.
