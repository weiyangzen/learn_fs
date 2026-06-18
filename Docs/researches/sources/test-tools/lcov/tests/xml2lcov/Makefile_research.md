# sources/test-tools/lcov/tests/xml2lcov/Makefile

## Purpose

This Makefile registers the XML-to-LCOV conversion test script for the shared harness.

## Important APIs, types, and functions

It includes `../common.mak`, sets `TESTS := xml2lcov.sh`, and delegates cleanup to `./xml2lcov.sh --clean`.

## Control flow

The shared harness will run `xml2lcov.sh` if present in the test directory. This file does not contain converter logic itself.

## State and persistence behavior

No state is managed in the Makefile. Cleanup is delegated to the shell script.

## Dependencies and integration points

It depends on `common.mak` and the `xml2lcov.sh` test script, which is outside this specific work item but expected by the test suite.

## Risks and test signals

The Makefile can fail if `xml2lcov.sh` is missing, not executable, or changes its cleanup interface. Otherwise, its signal is simply harness registration.
