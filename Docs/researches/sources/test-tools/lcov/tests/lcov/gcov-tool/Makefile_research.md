# sources/test-tools/lcov/tests/lcov/gcov-tool/Makefile

## Purpose

This Makefile registers the relative/absolute `--gcov-tool` path-resolution test.

## Important APIs, types, and functions

It includes `../../common.mak`, sets `TESTS := path.sh`, and has a `clean` recipe removing `test`, `.info`, `.gcda`, and `.gcno` artifacts.

## Control flow

Test execution is delegated to the shared harness. Cleanup is local because the artifacts are simple compiler and LCOV outputs.

## State and persistence behavior

The file creates no state itself. Its clean recipe removes compiled and coverage products from the test directory.

## Dependencies and integration points

It depends on `common.mak` and on `path.sh` for the actual `--gcov-tool` coverage.

## Risks and test signals

The clean rule is intentionally narrow; if `path.sh` grows additional logs or helper outputs, the clean target may need to be updated.
