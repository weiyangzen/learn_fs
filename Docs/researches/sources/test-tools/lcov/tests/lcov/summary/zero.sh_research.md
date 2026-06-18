# sources/test-tools/lcov/tests/lcov/summary/zero.sh

## Purpose

`zero.sh` validates `lcov --summary` output for a zero-coverage fixture.

## Important APIs, types, and functions

It parses local coverage/verbose options, runs `$LCOV --summary "${ZEROINFO}"`, filters `Devel::Cover` stderr through process substitution, and validates `ZEROCOUNTS` with `check_counts`.

## Control flow

The script summarizes the zero-coverage fixture, captures and prints stdout/stderr logs, enforces zero exit status unless in coverage keep-going mode, requires stdout, rejects unexpected stderr, and checks counts.

## State and persistence behavior

It writes `summary_zero_stdout.log` and `summary_zero_stderr.log`.

## Dependencies and integration points

It depends on `$ZEROINFO`, `$ZEROCOUNTS`, `$LCOV`, and `check_counts` from the summary harness.

## Risks and test signals

The important signal is exact reporting of zero hit counts/rates. The stderr redirection is slightly different from sibling scripts and could be fragile if shell behavior changes.
