# sources/storage-engines/rocksdb/crash_test.mk

## Purpose
Makefile for RocksDB crash-test orchestration. It supports direct `make -f crash_test.mk` use and inclusion from the main Makefile.

## Important APIs and Control Flow
`DB_STRESS_CMD` defaults to `./db_stress`, and `common.mk` supplies `PYTHON` and `TEST_TMPDIR`. TSAN runs export suppressions. `CRASHTEST_PY` invokes `tools/db_crashtest.py` with stress command, cleanup command, and `--destroy_db_initially=1`. Phony aggregate targets run whitebox and blackbox variants for atomic flush, transaction write policies, timestamp support, optimistic transactions, tiered storage, multi-ops transactions, and best-efforts recovery. Whitebox tests add `--random_kill_odd`, defaulting to `888887`. `crash_test_db_cleanup` delegates deletion to `db_stress`.

## State, Dependencies, and Risks
The file creates and destroys DB state under `TEST_TMPDIR`, relies on a built `db_stress`, and forwards `CRASH_TEST_EXT_ARGS`. Risks include accidental parallelization of sequences marked "Do not parallelize", old deprecated target aliases, shell quoting of cleanup command, and feature coverage depending on `db_stress` options staying compatible. Test signal is successful blackbox/whitebox crash-test execution.
