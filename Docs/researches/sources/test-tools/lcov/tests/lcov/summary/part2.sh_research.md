# sources/test-tools/lcov/tests/lcov/summary/part2.sh

## Purpose

`part2.sh` validates `lcov --summary` output for the second partial coverage fixture.

## Important APIs, types, and functions

It parses local coverage/verbose options, captures `summary_part2_stdout.log` and stderr log, runs `$LCOV --summary "${PART2INFO}"`, and checks counts with `$PART2COUNTS`.

## Control flow

The script summarizes the part-two fixture, validates exit status and output streams, and checks expected summary counts.

## State and persistence behavior

It writes logs but no persistent coverage data.

## Dependencies and integration points

It depends on the summary harness for fixture path, count expectations, and helper functions.

## Risks and test signals

Like part one, this script is disabled in normal runs. Its signal is exact count matching for one partial profile.
