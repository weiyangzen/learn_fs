# sources/storage-engines/sqlite/ext/fts3/tool/fts3cov.sh

## Purpose
`fts3cov.sh` is a small developer coverage helper for the SQLite FTS3 extension. It runs the FTS3 Tcl test suite under `testfixture`, then prints branch-coverage summaries from `gcov` for each C file under `ext/fts3`.

## Important APIs, Types, And Functions
This is a POSIX shell script, not a library. It uses `set -e` to stop on unhandled command failures, computes `srcdir` by walking four directories up from `$0`, runs `./testfixture $srcdir/test/fts3.test --output=fts3cov-out.txt`, and loops over `ext/fts3/*.c` basenames to run `gcov -b`.

The output filter prints each C filename followed by the `gcov` branch line after removing the `Taken at least once:` prefix.

## Control Flow
The script assumes it is launched from a build directory containing `./testfixture` and coverage files for the FTS3 C objects. It computes the source root, executes `test/fts3.test`, emits a blank line, then iterates over all FTS3 C files by basename. For each file it prints `<file>: ` and appends the branch coverage percentage reported by `gcov -b`.

Because `set -e` is active, failure to run the test fixture, `gcov`, or the filtering pipeline can terminate the script.

## State And Persistence Behavior
The script writes `fts3cov-out.txt` in the current directory and relies on coverage data files created by prior or current test execution. It does not modify source files or SQLite databases intentionally. `gcov` may emit `.gcov` files as side effects in the working directory depending on toolchain behavior.

## Dependencies
Dependencies are `/bin/sh`, `dirname`, `ls`, `basename`, `gcov`, `grep`, `sed`, a coverage-instrumented SQLite build, and a working `testfixture` binary. The source tree must have `test/fts3.test` and `ext/fts3/*.c` relative to the computed root.

## Integration Points
It integrates with SQLite's Tcl test harness and GCC/gcov-style coverage workflow. It is specifically aimed at FTS3/FTS4 C sources and complements the main test suite by summarizing branch coverage after `fts3.test`.

## Risks And Edge Cases
The path calculation and unquoted command substitutions are brittle for paths containing whitespace. `echo -ne` is not portable across all `/bin/sh` implementations. The `ls | for` pattern can mishandle unusual filenames, though SQLite source filenames are stable and simple. The script assumes `gcov` can locate coverage notes by basename from the current directory; out-of-tree builds may need different `gcov` options.

## Test Signals
A useful validation is to run it from a coverage-enabled SQLite build directory and confirm `fts3cov-out.txt` is produced and each FTS3 C file prints a branch coverage percentage. Failures generally indicate missing testfixture, missing coverage instrumentation, wrong working directory, or gcov version/path mismatch.
