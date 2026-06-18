# sources/storage-engines/wiredtiger/test/huge/smoke.sh

Purpose: smoke wrapper for the huge-item test.

Important behavior: the script enables `set -e` and runs `$TEST_WRAPPER ./t -s`. The `-s` flag maps to the small runtime path in `huge.c`, and `$TEST_WRAPPER` lets the surrounding test harness inject environment, timeout, sanitizer, or platform wrappers.

Control flow and state: there is no persistent state in the script. The underlying test creates and removes its own WiredTiger test home.

Dependencies and integration: expects to run in the directory where `./t` is the huge test executable or wrapper target. It is intended for `make check` style smoke execution, complementing the CMake `small|-s` variant.

Risks and test signals: any nonzero exit fails the smoke due to `set -e`. The script only exercises bounded huge-item coverage, so regressions specific to multi-gigabyte sizes require explicit full test runs.
