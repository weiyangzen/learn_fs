# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/matchers/_doctest.py

Purpose: matcher that reuses doctest output comparison rules for assertion output.

Important APIs, types, and functions: `_NonManglingOutputChecker` subclasses `doctest.OutputChecker` to avoid Python unicode/ascii mangling. `DocTestMatches(example, flags=0)` stores wanted output with a trailing newline and compares actual output with doctest flags. `DocTestMismatch` delegates difference description to the checker.

Control flow: matching coerces actual output to the same string class as wanted, appends a newline if absent, and calls `check_output()`. On failure it returns `DocTestMismatch`, whose description is doctest's formatted output difference.

State and persistence: matcher stores desired output and flags. No external state.

Dependencies and integration points: depends on `doctest`, `re`, and core `Mismatch`. Useful where doctest ellipsis/whitespace semantics are needed inside `assertThat`.

Risks and test signals: compatibility hack references Python 2 attributes when present; modern Python paths rely on `_toAscii` override. Test signals are exact matches, `doctest.ELLIPSIS`, newline normalization, and unicode output preservation.
