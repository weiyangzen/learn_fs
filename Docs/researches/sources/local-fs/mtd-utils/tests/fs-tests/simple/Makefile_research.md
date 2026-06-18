# File Research: sources/local-fs/mtd-utils/tests/fs-tests/simple/Makefile

## Purpose
Builds simple standalone filesystem tests.

## Key Elements
Targets `test_1`, `test_2`, `ftrunc`, `orph`, and `perf`, all linked with `../lib/tests.o`. The `tests` target runs them with selected sync options.

## Dependencies
Uses `gcc`, shared `../lib/tests.o`, and include path `../lib`.

## Behavior/Risks
The `tests` target runs destructive filesystem tests immediately against the configured test mount.
