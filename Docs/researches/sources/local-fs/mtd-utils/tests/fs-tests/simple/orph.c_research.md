# File Research: sources/local-fs/mtd-utils/tests/fs-tests/simple/orph.c

## Purpose
Exercises open-but-unlinked orphan file handling.

## Key Elements
Creates `orph_test_dir_<pid>`, repeatedly creates up to one million unlinked open files, writes deterministic fragment data, verifies all open orphan contents, optionally fills remaining space through the last descriptor, sleeps, closes descriptors, and repeats.

## Dependencies
Uses shared orphan/fragment helpers from `tests.h`.

## Behavior/Risks
Can exhaust file descriptors or filesystem space by design. It expects `ENOSPC` or `EMFILE` as stopping conditions and requires cleanup by closing all orphan fds.
