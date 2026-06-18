# sources/test-tools/lcov/tests/lcov/merge/merge.sh

## Purpose

`merge.sh` tests LCOV tracefile set operations and merge edge cases: intersection, subtraction, generated line coverpoints from MC/DC data, function merge summaries, and duplicate-function diagnostics.

## Important APIs, types, and functions

It uses `LCOV_TOOL` with `--branch`, `--mcdc-coverage`, `--intersect`, `--subtract`, and `-a`. It compares outputs against `intersect.gold`, `a_subtract_b.gold`, and `b_subtract_a.gold`. It checks records such as `DA:6,0`, `LF:8`, `LH:2`, `FNF:2`, and `FNH:2`, and logs inconsistent duplicate-function messages via `--msg-log inconsistent.log`.

## Control flow

After cleanup and prerequisite checks, the script computes `a.info intersect b.info` and `b.info intersect a.info`, verifies reflexive equality, and compares with the golden file. It computes both subtraction directions and checks each against its golden output. It then verifies glob patterns with no matching files fail in both left and right operand positions. Later it adds `mcdc.dat` and checks generated line totals, merges two function-bug fixtures and validates function totals, and merges inconsistent data while requiring a duplicate function diagnostic in the message log.

## State and persistence behavior

It writes multiple `.info` outputs and logs, removes report and temp artifacts, and accumulates `status` across checks. It uses fixture `.info`, `.dat`, and `.gold` files as stable inputs.

## Dependencies and integration points

It depends on LCOV's tracefile algebra, parser tolerance via `--ignore inconsistent,empty`, MC/DC-to-line synthesis, and function identity merge logic. It integrates with message logging to validate diagnostics rather than only output records.

## Risks and test signals

Set-operation output ordering must remain stable for `diff`-based golden comparisons. The strongest signals are commutative intersection, directional subtraction goldens, failure on unmatched globs, correct synthesized DA/LF/LH records, and duplicate-function diagnostics.
