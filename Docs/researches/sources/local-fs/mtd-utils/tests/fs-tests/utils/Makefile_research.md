# File Research: sources/local-fs/mtd-utils/tests/fs-tests/utils/Makefile

## Purpose
Builds utility programs for fs-tests.

## Key Elements
Targets `fstest_monitor` and `free_space`, with a `tests` target that runs both lightly.

## Dependencies
Uses `gcc` and include path `../lib`, though these utilities do not link the shared test object.

## Behavior/Risks
The `tests` target invokes `fstest_monitor` with no child programs and `free_space` for the current filesystem.
