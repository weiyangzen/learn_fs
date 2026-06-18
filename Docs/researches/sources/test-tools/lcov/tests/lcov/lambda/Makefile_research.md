# sources/test-tools/lcov/tests/lcov/lambda/Makefile

## Purpose

This Makefile registers the lambda-function tracefile merge/filtering test.

## Important APIs, types, and functions

It includes `../../common.mak`, sets `TESTS := lambda.sh`, and delegates cleanup to `./lambda.sh --clean`.

## Control flow

The shared harness runs `lambda.sh`; cleanup is handled through the script.

## State and persistence behavior

No independent state is maintained by the Makefile.

## Dependencies and integration points

It depends on `common.mak` and `lambda.sh`.

## Risks and test signals

Make-level risk is minimal; substantive pass/fail behavior is entirely in `lambda.sh`.
