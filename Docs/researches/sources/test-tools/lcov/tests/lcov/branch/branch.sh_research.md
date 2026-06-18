<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/branch/branch.sh -->
# sources/test-tools/lcov/tests/lcov/branch/branch.sh

- Purpose: Shell helper or test driver for `sources/test-tools/lcov/tests/lcov/branch`.
- Important APIs/types/functions: Executable script interface; local functions are absent or limited to driver helpers parsed by the script itself.
- Control flow: Parses optional test flags, invokes lcov/genhtml/compiler/helper commands, and checks results with exit codes, `grep`, `diff`, or generated file existence.
- State and persistence behavior: Creates transient logs, coverage files, binaries, and output directories named in its cleanup block or parent Makefile.
- Dependencies and integration points: Depends on `common.tst` where sourced, local fixtures, lcov/genhtml tools, compiler tools, and standard shell utilities.
- Risks: Risks are exact diagnostic greps, environment/tool availability, and stale cleanup lists.
- Test signals: Passing signals are successful expected commands and explicit grep/diff/file-existence assertions.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/branch/branch.sh -->
