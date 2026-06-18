# sources/test-tools/lcov/tests/lcov/mcdc/Makefile

## Purpose

This Makefile registers the GCC/LLVM MC/DC coverage interoperability test.

## Important APIs, types, and functions

It includes `../../common.mak`, sets `TESTS := mcdc.sh`, and delegates cleanup to `./mcdc.sh --clean`.

## Control flow

The common harness runs `mcdc.sh`; the clean target asks the script to remove generated coverage, JSON, reports, and binaries.

## State and persistence behavior

The Makefile owns no persistent state.

## Dependencies and integration points

It depends on the shared LCOV make harness and on the compiler-sensitive `mcdc.sh`.

## Risks and test signals

No independent test logic exists here; risks are limited to cleanup delegation style.
