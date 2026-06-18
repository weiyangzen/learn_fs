# sources/test-tools/lcov/tests/lcov/misc/version.sh

## Purpose

`version.sh` verifies that `lcov --version` exits successfully, writes version text to stdout, and keeps stderr clean outside coverage instrumentation.

## Important APIs, types, and functions

It sources `../../common.tst`, uses `LCOV`, `KEEP_GOING`, and `COVER`, captures stdout and filtered stderr to `version_stdout.log` and `version_stderr.log`.

## Control flow

The script runs `$LCOV --version`, prints captured output, checks the return code, requires non-empty stdout, and rejects stderr unless `COVER` is set.

## State and persistence behavior

It writes log files only.

## Dependencies and integration points

It depends on the harness-provided `LCOV` command and Bash process substitution. It integrates with coverage-mode stderr filtering.

## Risks and test signals

The test is intentionally broad; it does not parse the version string, so its signal is command health and stream discipline rather than semantic version correctness.
