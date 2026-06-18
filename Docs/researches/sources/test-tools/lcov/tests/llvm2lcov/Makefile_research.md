# sources/test-tools/lcov/tests/llvm2lcov/Makefile

## Purpose

This Makefile registers the standalone `llvm2lcov` conversion test.

## Important APIs, types, and functions

It includes `../common.mak`, sets `TESTS := llvm2lcov.sh`, and delegates cleanup to `./llvm2lcov.sh --clean`.

## Control flow

The common test harness executes the shell script. Cleanup delegates to the script because it owns generated LLVM profile, JSON, info, and report artifacts.

## State and persistence behavior

The Makefile has no independent state.

## Dependencies and integration points

It depends on the LCOV test harness and `llvm2lcov.sh`.

## Risks and test signals

Make-level risk is minimal; compiler/tool-version sensitivity is handled by the script.
