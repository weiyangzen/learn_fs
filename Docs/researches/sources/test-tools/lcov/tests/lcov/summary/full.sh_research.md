# sources/test-tools/lcov/tests/lcov/summary/full.sh

## Purpose

`full.sh` validates `lcov --summary` output for a fixture expected to report full coverage.

## Important APIs, types, and functions

It parses local `--coverage` and `--verbose`, captures stdout/stderr into `summary_full_*` logs, runs `$LCOV --summary "${FULLINFO}"`, and calls `check_counts "$FULLCOUNTS"`.

## Control flow

The script handles optional Devel::Cover wrapping, runs summary on `$FULLINFO`, prints captured output, checks exit status and streams, and compares output counts with `$FULLCOUNTS`.

## State and persistence behavior

It writes only logs. It uses `KEEP_GOING` to allow coverage-instrumented runs to continue after non-zero return codes.

## Dependencies and integration points

It relies on the summary harness for `$LCOV`, `$FULLINFO`, `$FULLCOUNTS`, and `check_counts`.

## Risks and test signals

The primary signal is exact summary-count formatting and values for a 100-percent coverage profile. Stream checks catch regressions in CLI output behavior.
