# File Research: sources/local-fs/mtd-utils/tests/fs-tests/simple/test_1.c

## Purpose
Tests filesystem behavior when a large unlinked file remains open while the FS is filled.

## Key Elements
Creates a half-free-space `big_file`, opens it, edits beginning/end sentinels, unlinks it, fills the directory with smaller files until full, checks the open deleted file, deletes the filler files, restores original bytes/truncates, verifies data, closes the orphan, and removes the test directory.

## Dependencies
Uses shared fill/check/delete helpers and optional sync support from `tests.h`.

## Behavior/Risks
Intentionally fills the filesystem and relies on open deleted-file accounting. It destructively creates and removes many `fill_up_N` files.
