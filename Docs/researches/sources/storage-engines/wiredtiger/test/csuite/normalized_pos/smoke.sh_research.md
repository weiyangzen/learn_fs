# sources/storage-engines/wiredtiger/test/csuite/normalized_pos/smoke.sh

Purpose: shell smoke wrapper for the normalized position csuite test.

Important APIs, types, and functions: uses POSIX `sh`, `set -e`, optional binary path argument, `binary_dir` fallback to `dirname $0`, and `TEST_WRAPPER`.

Control flow: resolves the binary either from `$1` or `$binary_dir/normalized_pos`, then runs it under `$TEST_WRAPPER` with no additional options. Any nonzero exit fails because `set -e` is active.

State and persistence behavior: the wrapper writes no state. The binary creates and removes `WT_TEST.normalized_pos`.

Dependencies and integration points: registered by `CMakeLists.txt` as the `EXEC_SCRIPT` for `test_normalized_pos`. The default binary name in the script is `normalized_pos`, so build-system target/binary naming must match the copied script environment.

Risks: direct source-tree execution without a binary argument can resolve an invalid binary path. The wrapper does not pass `-v`, so detailed npos trace output is disabled in normal smoke runs.

Test signals: zero exit from the normalized-position binary validates both in-memory and on-disk internal npos paths.
