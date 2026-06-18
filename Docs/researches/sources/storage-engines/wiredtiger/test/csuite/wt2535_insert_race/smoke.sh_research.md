# sources/storage-engines/wiredtiger/test/csuite/wt2535_insert_race/smoke.sh

Purpose: this wrapper runs the WT-2535 insert race test in both supported table layouts.

Important APIs and variables: it uses POSIX `sh`, `set -e`, optional positional binary path, `binary_dir` fallback, and `TEST_WRAPPER`. The default binary is `test_wt2535_insert_race`.

Control flow: after resolving the binary, it runs `$TEST_WRAPPER $test_bin -t r` for row-store and `$TEST_WRAPPER $test_bin -t c` for column-store. The C test supplies its own default thread and operation counts.

State and persistence behavior: no wrapper state is persisted. The C test creates a temporary table, performs concurrent updates to one record, validates the final value, and cleans up on success.

Dependencies and integration points: it assumes the test utility `-t` table-type option accepts `r` and `c`. It is intended for make-check style execution through `TEST_WRAPPER`.

Risks and test signals: the wrapper signal is exit status. It provides focused row/column correctness coverage but does not vary thread count, record count, or cache settings.
