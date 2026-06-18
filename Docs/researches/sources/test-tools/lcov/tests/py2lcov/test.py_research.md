# sources/test-tools/lcov/tests/py2lcov/test.py

## Purpose

`test.py` is the Python fixture executed under Coverage.py for `py2lcov` tests. It defines nested functions to exercise function-range extraction and uses LCOV exclusion markers around the module entrypoint.

## Important APIs, types, and functions

It imports `localmodule`, defines `main()`, and inside `main` defines `localfunc()`, `nested1()`, and `nested2()`. The `if __name__ == '__main__': main()` block is wrapped in `LCOV_EXCL_START/STOP`.

## Control flow

When run as a script, it calls `main()`. `main` prints, calls `localmodule.enter("hello world", 1, 2)`, defines but does not call `localfunc`, and returns implicitly. The nested functions are never executed, providing zero-hit function expectations.

## State and persistence behavior

No persistent state is stored. Coverage.py records executed and unexecuted lines/functions externally.

## Dependencies and integration points

It depends on sibling `localmodule.py`. `py2lcov.sh` asserts exact zero-hit lines and nested function names/ranges derived from this file.

## Risks and test signals

Line numbers and nested definitions are fixture API. Reformatting or executing the nested functions changes expected `DA`, `FNL`, and `FNA` records.
