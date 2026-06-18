# sources/test-tools/lcov/tests/lcov/gcov-tool/mygcov.sh

## Purpose

`mygcov.sh` is a minimal wrapper used to verify that LCOV and geninfo can execute a user-specified gcov tool by absolute or relative path.

## Important APIs, types, and functions

The script contains one command: `exec gcov "$@"`. `exec` replaces the wrapper process, preserving gcov's exit code and argument handling.

## Control flow

There is no branching. All arguments from the caller are forwarded directly to `gcov`.

## State and persistence behavior

The wrapper maintains no state and writes no files itself. Any outputs are produced by `gcov`.

## Dependencies and integration points

It depends on `gcov` being available on `PATH`. It integrates with `path.sh`, which passes this script as the `--gcov-tool` value.

## Risks and test signals

Because it is deliberately transparent, any failure indicates path execution or gcov availability rather than wrapper logic. Executable permissions are part of the practical test surface.
