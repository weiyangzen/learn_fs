# sources/test-tools/lcov/tests/lcov/lambda/lambda.sh

## Purpose

`lambda.sh` tests LCOV handling of lambda function extents in prebuilt trace data, especially merging duplicate lambda records and deriving the expected function end line.

## Important APIs, types, and functions

It sources `common.tst`, uses `LCOV_TOOL`, `COVER`, `LCOV_OPTS="--branch $PARALLEL $PROFILE"`, and runs `lcov -a 'lambda*.dat' -o filter.info`. It checks `FNL:` records with `grep -E`.

## Control flow

After cleanup, the script merges all `lambda*.dat` fixtures into `filter.info`. It asserts exactly one function-location record ending at line 319, which indicates two lambda records were merged. It also checks that `toArrayOf` has the derived function extent `FNL:...,303,309`.

## State and persistence behavior

The script removes text, JSON, reports, compiled artifacts, gcov files, and `.info` outputs. It produces `filter.info` and optional local coverage outputs.

## Dependencies and integration points

It depends on fixture files matching `lambda*.dat`, LCOV function merge logic, branch mode, and the common harness.

## Risks and test signals

The test relies on fixed line numbers in the fixtures. The important signals are successful aggregation and exact `FNL` records proving lambda merge and function-end derivation behavior.
