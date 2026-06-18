# sources/storage-engines/wiredtiger/test/csuite/incr_backup/smoke.sh

Purpose: shell smoke wrapper for `test_incr_backup` as part of `make check`/CTest.

Important APIs, types, and functions: the script uses POSIX `sh`, `set -e`, optional first argument for the test binary, `binary_dir=${binary_dir:-\`dirname $0\`}`, `TEST_WRAPPER`, and executes the resolved binary with `-v 3`.

Control flow: if `$1` is non-empty, it is treated as the binary path. Otherwise the script assumes it has been copied to the build directory and resolves `test_incr_backup` beside itself. It then runs `$TEST_WRAPPER $test_bin -v 3`; `set -e` makes any nonzero exit fail the smoke test.

State and persistence behavior: the script itself writes no files, but the test binary creates and removes or preserves `WT_TEST.incr_backup` and backup artifacts depending on binary options. It raises verbosity enough to expose backup progress.

Dependencies and integration points: copied by `CMakeLists.txt` through `define_c_test(EXEC_SCRIPT ...)`, depends on `TEST_WRAPPER` when supplied by the harness, and assumes build-directory layout for default binary discovery.

Risks: running the source-tree script directly without passing a binary can resolve the wrong path because the fallback assumes build-directory placement. Backtick command substitution is portable but old style.

Test signals: successful smoke execution is simply a zero exit from the verbose incremental backup randomized test.
