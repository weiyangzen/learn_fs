# sources/storage-engines/wiredtiger/test/csuite/truncated_log/smoke.sh

Purpose: this wrapper smoke-tests the truncated log recovery program in both row-store and column-store modes.

Important APIs and variables: it uses POSIX `sh`, `set -e`, an optional positional binary path, `binary_dir` fallback, and `TEST_WRAPPER`. The default binary is `test_truncated_log`.

Control flow: after resolving the binary, it runs `$TEST_WRAPPER $test_bin` and `$TEST_WRAPPER $test_bin -c`. The first exercises default string-key row-store; the second exercises recno column-store.

State and persistence behavior: the wrapper does not persist state. The C test creates, corrupts, recovers, and removes its own work directory unless preservation is requested through direct options.

Dependencies and integration points: it is intended for `make check` and assumes the script is copied near the built binary or receives the binary path as an argument.

Risks and test signals: the signal is exit status. The script only covers the two table formats; logging and recovery behavior are fixed by the C test.
