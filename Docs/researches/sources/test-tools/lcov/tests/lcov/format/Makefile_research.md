# sources/test-tools/lcov/tests/lcov/format/Makefile

## Purpose

This Makefile registers the `format.sh` LCOV tracefile-format test with the shared LCOV test harness.

## Important APIs, types, and functions

It includes `../../common.mak`, sets `TESTS := format.sh`, and implements `clean` by invoking `./format.sh --clean` through `$(shell ...)`.

## Control flow

The shared makefile owns normal test dispatch. This file only contributes the test list and delegates cleanup to the script, keeping cleanup logic close to the artifacts `format.sh` creates.

## State and persistence behavior

No independent state is maintained. The clean target relies on the script to remove `.info`, logs, gcov files, JSON, and temporary outputs.

## Dependencies and integration points

It depends on `common.mak` for test-runner targets and on `format.sh` for both execution and cleanup behavior.

## Risks and test signals

The use of `$(shell ...)` means cleanup runs during make expansion rather than as a normal recipe command, matching this suite's pattern but making error propagation weaker than a standard shell recipe.
