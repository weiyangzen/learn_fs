# sources/test-tools/lcov/tests/lcov/summary/concatenated2.sh

## Purpose

`concatenated2.sh` checks that concatenating two partial coverage files produces target summary counts.

## Important APIs, types, and functions

It parses the same local `--coverage` and `--verbose` options, writes `summary_concatenated2_stdout.log` and stderr log, creates `concatenated2.info` from `$PART1INFO` and `$PART2INFO`, runs `$LCOV --summary`, and validates with `check_counts "$TARGETCOUNTS"`.

## Control flow

After option parsing, it concatenates the partial inputs, summarizes the result, validates zero exit code unless in keep-going coverage mode, requires stdout, rejects unexpected stderr, and checks counts.

## State and persistence behavior

The script writes a generated combined info file and logs.

## Dependencies and integration points

It depends on generated partial fixtures and shared summary-harness functions/variables.

## Risks and test signals

The test is disabled in the Makefile due to inconsistent generated data. Its intended signal is additive equivalence of partial coverage summaries to the target profile.
