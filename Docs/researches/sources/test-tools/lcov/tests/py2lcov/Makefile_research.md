# sources/test-tools/lcov/tests/py2lcov/Makefile

## Purpose

This Makefile registers the Python Coverage.py-to-LCOV conversion test.

## Important APIs, types, and functions

It includes `../common.mak`, sets `TESTS := py2lcov.sh`, and delegates cleanup to `./py2lcov.sh --clean`.

## Control flow

The common harness runs `py2lcov.sh`, and cleanup is script-owned.

## State and persistence behavior

No independent state is maintained.

## Dependencies and integration points

It depends on `common.mak`, Python coverage tooling, and `py2lcov.sh`.

## Risks and test signals

The Makefile is simple; converter and environment complexity lives in the script.
