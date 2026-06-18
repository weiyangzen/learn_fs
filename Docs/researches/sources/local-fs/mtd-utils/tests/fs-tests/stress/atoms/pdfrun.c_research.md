# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/pdfrun.c

## Purpose
Creates/overwrites a large file in the current directory, but only if current directory is not on the test filesystem.

## Key Elements
Caps requested size to half of total memory from `/proc/meminfo`, creates `run_pdf_test_file_<pid>`, repeatedly writes PID-seeded random data, rewinds between repeats, then closes and unlinks.

## Dependencies
Uses POSIX file APIs, `/proc/meminfo`, and shared current-FS helper.

## Behavior/Risks
No-op when the current directory is on the test FS. Intended to create external write pressure during test-FS stress.
