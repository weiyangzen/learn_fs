# sources/test-tools/lcov/tests/lcov/summary/target.sh

## Purpose

`target.sh` validates summary output for a target coverage file whose rates are generated from an mkinfo profile.

## Important APIs, types, and functions

It uses the shared local option parser, runs `$LCOV --summary "${TARGETINFO}"`, captures `summary_target_*` logs, and validates `TARGETCOUNTS` through `check_counts`.

## Control flow

The script parses optional coverage/verbose flags, runs summary on the target fixture, enforces exit status and stream expectations, then checks counts.

## State and persistence behavior

It creates log files only.

## Dependencies and integration points

It depends on generated target fixture variables from the summary harness and the LCOV summary command.

## Risks and test signals

The Makefile disables it because fixture data is inconsistent. Its intended signal is exact summary formatting and rates for a generated target profile.
