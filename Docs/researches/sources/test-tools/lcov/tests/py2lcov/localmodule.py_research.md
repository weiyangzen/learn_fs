# sources/test-tools/lcov/tests/py2lcov/localmodule.py

## Purpose

`localmodule.py` is a Python fixture module for `py2lcov`, providing an exercised function, a branch exclusion region, and an unused function.

## Important APIs, types, and functions

It defines `enter(s, a, b)` and `unusedFunc()`. `enter` prints its argument and contains `LCOV_EXCL_BR_START/STOP` around an `if a:` branch. `unusedFunc` prints and returns `1` but is not called by the test program.

## Control flow

`enter` always prints, and when `a` is true also prints branch text. `unusedFunc` is straight-line code.

## State and persistence behavior

The module has no persistent state. Coverage.py records execution externally.

## Dependencies and integration points

It is imported by `test.py` and converted by `py2lcov.sh`, which checks function records and branch-region filtering.

## Risks and test signals

The typo-like output string `lcocalmodule::enter` is harmless but fixture output should not be treated as API. Function line numbers and exclusion markers are part of coverage expectations.
