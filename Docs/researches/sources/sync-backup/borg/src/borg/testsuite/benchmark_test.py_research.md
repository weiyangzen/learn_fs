<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/benchmark_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/benchmark_test.py

Purpose: pytest-benchmark performance tests for common Borg CLI commands and propdict item attribute access.

Important APIs: `benchmark`, `cmd_fixture`, `changedir`, fixtures `repo_url`, `repo`, `testdata`, `repo_archive`, `Item`, and `zeros`.

Control flow: fixtures set isolated repository/cache/key env vars and create repositories under encryption modes `none` and `aes-ocb`; session test data is either zero-like memoryview content or `os.urandom`. Benchmarks time `create` with no compression/lz4, `extract`, `delete`, `list`, `info`, `check`, `help`, and attribute set/get/as_dict on `Item`.

State and persistence: creates temporary repositories, cache/key dirs, test data directories, and archives. Cleanup removes tmp dirs through fixture finalizers.

Dependencies/integration: depends on pytest-benchmark plugin, command fixture return conventions, compression support, and generated data size. Risks include high disk/CPU use, sparse detection avoidance via non-binary-zero memoryview, and benchmark-only semantics not being normal correctness tests. Test signals are command result code `0` and propdict attribute equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/benchmark_test.py -->
