# sources/test-tools/lcov/tests/perl2lcov/example.pl

## Purpose

`example.pl` is the Perl coverage fixture for `perl2lcov`. It creates global and package-scoped subroutines, exercised and unexercised branches, and LCOV exclusion markers.

## Important APIs, types, and functions

It uses `strict`, defines `global1`, package `space1` with `packageFunc` and `packageFunc2`, package `space2` with `packageFunc` and `packageFunc2`, and main-package code. It includes `LCOV_EXCL_START/STOP` around one function and `LCOV_EXCL_BR_START/STOP` around main-package branch-related code.

## Control flow

The main package prints a message, calls `global1`, calls `space1::packageFunc2(1)`, calls `space2::packageFunc()`, and enters an `unless (@ARGV)` branch when no arguments are passed. Several branches depend on nonexistent environment variables so they remain unhit.

## State and persistence behavior

The program reads environment variables and command-line arguments but stores no persistent state. Devel::Cover records execution data externally when run by the test script.

## Dependencies and integration points

It depends on Perl and Devel::Cover instrumentation. It integrates with `perltest1.sh`, which verifies function names, namespaces, line/branch records, region filtering, branch-region filtering, and checksum output.

## Risks and test signals

Package/function names and LCOV exclusion comments are part of the fixture contract. Reordering functions can change expected `FNA` indexes and line counts.
