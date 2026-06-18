<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/history.sh -->
# sources/test-tools/lcov/tests/lcov/extract/history.sh

- Purpose: Trivial history callback for option plumbing tests.
- Important APIs/types/functions: Executable `/bin/sh` script prints an empty line.
- Control flow: Provides minimal successful callback output so callers reach the intended validation path.
- State and persistence behavior: No persistent state.
- Dependencies and integration points: Depends only on `/bin/sh` and history callback invocation.
- Risks: Future protocols may require structured output.
- Test signals: Passing signal is callers proceeding beyond helper execution.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/history.sh -->
