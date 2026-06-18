# sources/test-tools/lcov/tests/lcov/summary/Makefile

## Purpose

This Makefile registers LCOV summary-output tests for generated coverage profiles and explicitly disables older inconsistent summary fixtures.

## Important APIs, types, and functions

It includes `../../common.mak`, sets active `TESTS := zero.sh full.sh`, and records disabled scripts in `DISABLED := target.sh part1.sh part2.sh concatenated.sh concatenated2.sh`. The clean target removes `*.info` and `*.log`.

## Control flow

Only `zero.sh` and `full.sh` run by default. The disabled tests remain in the tree for reference but are not part of normal execution because their generated data has inconsistent line/branch/function hit/miss statistics.

## State and persistence behavior

The Makefile cleans generated summary logs and info files but has no runtime state.

## Dependencies and integration points

It depends on shared variables from `common.mak`, including generated info-file paths and count expectations used by the scripts.

## Risks and test signals

The disabled list is a maintenance signal: re-enabling those tests requires either consistent fixture generation or updated expectations. Active test signal comes from full and zero summary count checks.
