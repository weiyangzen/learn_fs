# sources/storage-engines/rocksdb/coverage/coverage_test.sh

## Purpose
Shell driver for generating textual and optional HTML code coverage reports from GCC/gcov output.

## Important APIs and Control Flow
The script exits on error and rejects `USE_CLANG`, because it supports GCC coverage only. It selects `gcov` from Meta-internal GCC when present or from `PATH`. It creates `COVERAGE_REPORT`, finds all `*.gcno` files under `..`, runs gcov with `--preserve-paths --relative-only --no-output`, pipes output through `parse_gcov_output.py`, and writes `coverage_report_all.txt`. It also derives files from `git show --name-only HEAD`, filters the parsed report with `-interested-files`, and writes `coverage_report_recent.txt`. If `HTML` is set and a supported `lcov` exists, it captures `coverage.info` and runs `genhtml`.

## State, Dependencies, and Risks
Persistent outputs are report files under `COVERAGE_REPORT`. Dependencies include gcov, Python, git, optionally lcov/genhtml. Risks include unquoted variables, legacy lcov version check expectations, and recent-file filtering based only on HEAD. Coverage validation is the script's own report generation.
