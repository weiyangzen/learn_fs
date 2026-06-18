# sources/test-tools/lcov/tests/lcov/multiple/Makefile

## Purpose

This Makefile registers the multiple-directory initial-capture test.

## Important APIs, types, and functions

It includes `../../common.mak`, sets `TESTS := multiple.sh`, and delegates cleanup to `./multiple.sh --clean`.

## Control flow

The shared harness runs `multiple.sh`; the clean target delegates to script cleanup.

## State and persistence behavior

No state is managed independently.

## Dependencies and integration points

It depends on `common.mak` and `multiple.sh`.

## Risks and test signals

The Makefile itself has minimal risk beyond cleanup delegation style.
