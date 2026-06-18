# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/fwrite00.c

## Purpose
Configurable file write stress atom.

## Key Elements
Creates `filestress00_test_file_<pid>`, optionally unlinks it while open, writes either full random data or sparse-hole marker bytes, optionally closes/reopens, sleeps, deletes, and repeats according to shared `-z/-n/-p/-u/-o/-c/-e` options.

## Dependencies
Uses POSIX file APIs and shared `tests.h`.

## Behavior/Risks
Intentionally handles `ENOSPC` as normal. In unlink mode it stresses open-deleted-file behavior; in hole mode it creates large sparse extents with marker writes every 10 MB.
