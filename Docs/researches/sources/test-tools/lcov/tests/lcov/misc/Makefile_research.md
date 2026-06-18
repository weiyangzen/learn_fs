# sources/test-tools/lcov/tests/lcov/misc/Makefile

## Purpose

This Makefile registers basic LCOV CLI smoke tests for help and version output.

## Important APIs, types, and functions

It includes `../../common.mak`, sets `TESTS := help.sh version.sh`, and removes `*.log` in `clean`.

## Control flow

The shared harness runs the two scripts. Cleanup is a simple local log removal.

## State and persistence behavior

Only log files produced by the scripts are cleaned.

## Dependencies and integration points

It depends on `common.mak`, `help.sh`, `version.sh`, and the `LCOV` executable configured by the harness.

## Risks and test signals

The Makefile is low risk; the tests ensure the command-line interface remains callable.
