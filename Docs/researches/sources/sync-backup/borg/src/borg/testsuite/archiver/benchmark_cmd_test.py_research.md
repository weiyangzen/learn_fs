# sources/sync-backup/borg/src/borg/testsuite/archiver/benchmark_cmd_test.py

Purpose: verifies the `borg benchmark` command in both CRUD and CPU modes, including human-readable and JSON output shapes.

Important APIs/types/functions: `test_benchmark_crud`, `test_benchmark_crud_json_lines`, `test_benchmark_cpu`, and `test_benchmark_cpu_json` use `cmd`, `RK_ENCRYPTION`, `json`, and environment variables `_BORG_BENCHMARK_CRUD_TEST` / `_BORG_BENCHMARK_CPU_TEST` to force small deterministic benchmark workloads.

Control flow: CRUD tests create a repository, set test-mode env var, run `benchmark crud`, and assert all eight operation/sample IDs appear. The JSON-lines variant filters merged stdout/stderr for JSON records, decodes eight entries, and validates id, command, sample metadata, timing, and I/O types. CPU tests set test mode, run `benchmark cpu`, and assert expected text sections or JSON categories.

State and persistence behavior: CRUD mode creates and mutates repository archives as part of benchmark operations. CPU mode is computational and writes no repository. Environment variables alter benchmark scale for tests.

Dependencies and integration points: covers the benchmark command, JSON serialization, compression/hash/encryption/chunker/msgpack benchmark category naming, and the shared archiver harness.

Risks: timing and I/O fields are expected to be positive, which can be brittle if a mocked or extremely fast path reports zero. Output section/category names are part of the tested contract.

Test signals: verifies benchmark command does meaningful work, emits all expected operation IDs, and maintains parseable machine output.
