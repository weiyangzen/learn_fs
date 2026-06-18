# sources/test-tools/lcov/tests/lcov/summary/part1.sh

## Purpose

`part1.sh` validates `lcov --summary` output for the first partial coverage fixture.

## Important APIs, types, and functions

It uses the standard summary-script option parser, captures logs, runs `$LCOV --summary "${PART1INFO}"`, and calls `check_counts "$PART1COUNTS"`.

## Control flow

After option parsing, it summarizes the part-one fixture, checks exit code and streams, then validates expected counts.

## State and persistence behavior

It writes stdout/stderr logs only.

## Dependencies and integration points

It depends on shared summary harness variables and `check_counts`.

## Risks and test signals

The test is currently disabled by the Makefile due to inconsistent generated data. Its intended signal is correct summary output for one partial profile.
