# sources/test-tools/lcov/tests/lcov/summary/concatenated.sh

## Purpose

`concatenated.sh` checks that summarizing two concatenated copies of the target coverage file yields the same counts as the target profile.

## Important APIs, types, and functions

It parses `--coverage` and `--verbose`, sets optional `COVER` for Perl `Devel::Cover`, writes `summary_concatenated_stdout.log` and `summary_concatenated_stderr.log`, builds `concatenated.info` from two copies of `$TARGETINFO`, runs `$LCOV --summary`, and calls `check_counts "$TARGETCOUNTS"`.

## Control flow

The script processes local options, concatenates the fixture twice, runs summary with `--ignore inconsistent,inconsistent`, validates exit status and output streams, then delegates count validation to `check_counts`.

## State and persistence behavior

It writes one generated `.info` file and two logs. It changes `KEEP_GOING` when coverage instrumentation mode is enabled.

## Dependencies and integration points

It depends on environment variables and helper functions supplied by the summary harness, especially `TARGETINFO`, `TARGETCOUNTS`, `LCOV`, and `check_counts`.

## Risks and test signals

The test is disabled by the Makefile because fixture consistency is known to be weak. If run manually, its key signal is idempotent summary counts under duplicate tracefile concatenation.
