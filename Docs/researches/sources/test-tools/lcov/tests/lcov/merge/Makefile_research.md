# sources/test-tools/lcov/tests/lcov/merge/Makefile

## Purpose

This Makefile registers the LCOV set-operation and merge-behavior test.

## Important APIs, types, and functions

It includes `../../common.mak`, sets `TESTS := merge.sh`, and delegates cleanup to `./merge.sh --clean`.

## Control flow

The shared harness executes `merge.sh`; cleanup is delegated to the script.

## State and persistence behavior

The Makefile does not maintain state.

## Dependencies and integration points

It depends on `common.mak` and `merge.sh`.

## Risks and test signals

The substantive risk is in `merge.sh`; this file only provides harness registration.
