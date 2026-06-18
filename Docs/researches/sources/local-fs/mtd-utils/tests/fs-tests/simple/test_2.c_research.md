# File Research: sources/local-fs/mtd-utils/tests/fs-tests/simple/test_2.c

## Purpose
Tests many small files plus one large unlinked open file under repeated overwrites.

## Key Elements
Creates up to 1000 fragment files, appending 400 bytes round-robin until full; deletes half; creates a large file using two-thirds of free space; opens and unlinks it; repeatedly overwrites small-file ranges and rewrites the big open file; validates all remaining files after each phase.

## Dependencies
Uses shared fragment and filled-file helpers from `tests.h`.

## Behavior/Risks
Heavy space-pressure and overwrite test. It assumes deterministic fragment data remains valid across partial overwrites by using the same per-file random sequence.
