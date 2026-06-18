# sources/test-tools/lcov/tests/lcov/misc/help.sh

## Purpose

`help.sh` verifies that `lcov --help` exits successfully, writes user-facing content to stdout, and does not emit stderr noise outside coverage instrumentation.

## Important APIs, types, and functions

It sources `../../common.tst`, uses `LCOV`, `KEEP_GOING`, and `COVER`, captures stdout to `help_stdout.log`, and filters `Devel::Cover:` lines from stderr into `help_stderr.log` using process substitution.

## Control flow

The script runs `$LCOV --help`, captures the return code, prints captured logs, then checks three conditions: zero exit status unless `KEEP_GOING` is active, non-empty stdout, and empty stderr when not running under coverage.

## State and persistence behavior

It writes two log files. No cleanup is performed inside the script; the Makefile clean target removes logs.

## Dependencies and integration points

It depends on Bash process substitution and the harness-provided `LCOV` path. It accounts for `Devel::Cover` instrumentation output so coverage runs do not fail on known stderr text.

## Risks and test signals

The key signal is CLI availability and proper stream usage. If help output moves to stderr or becomes empty, this test fails.
