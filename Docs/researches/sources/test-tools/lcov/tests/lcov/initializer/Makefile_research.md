# sources/test-tools/lcov/tests/lcov/initializer/Makefile

## Purpose

This Makefile registers the initializer-list filtering test.

## Important APIs, types, and functions

It includes `../../common.mak`, sets `TESTS := initializer.sh`, and delegates cleanup to `./initializer.sh --clean`.

## Control flow

The shared harness runs the script. The local clean target keeps generated artifacts consistent with script cleanup.

## State and persistence behavior

No state is managed in the Makefile. Cleanup is delegated.

## Dependencies and integration points

It depends on the common LCOV test make rules and the `initializer.sh` script.

## Risks and test signals

As with similar Makefiles in this tree, cleanup via `$(shell ...)` may hide cleanup failures, but normal test signal comes from `initializer.sh`.
