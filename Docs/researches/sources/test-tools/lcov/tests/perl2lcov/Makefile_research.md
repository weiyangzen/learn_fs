# sources/test-tools/lcov/tests/perl2lcov/Makefile

## Purpose

This Makefile registers the Perl Devel::Cover-to-LCOV conversion test.

## Important APIs, types, and functions

It includes `../common.mak`, sets `TESTS := perltest1.sh`, and delegates cleanup to `./perltest1.sh --clean`.

## Control flow

The common harness runs `perltest1.sh`; cleanup is delegated to the script.

## State and persistence behavior

No independent state is maintained.

## Dependencies and integration points

It depends on `common.mak`, Perl tooling, and the test script.

## Risks and test signals

Make-level behavior is simple; substantive risks are Perl module availability and converter behavior.
