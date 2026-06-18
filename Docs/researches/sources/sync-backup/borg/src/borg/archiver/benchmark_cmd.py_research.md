# sources/sync-backup/borg/src/borg/archiver/benchmark_cmd.py

## Purpose
This module implements Borg's `benchmark` command group. `benchmark crud` measures end-to-end create, extract, update, and delete throughput against a repository using generated test files. `benchmark cpu` measures CPU-bound chunking, hashing/MAC, encryption, compression, and msgpack performance using in-memory data.

## Important APIs, Types, and Functions
- `BenchmarkMixIn.do_benchmark_crud(args)` orchestrates CRUD measurement.
- Nested `parse_args(args, cmd)` reparses internal Borg command invocations while propagating `--rsh` and `--remote-path`.
- Nested `measurement_run(repo, path)` invokes `do_create`, `do_delete`, and `do_extract` directly, times phases with `time.monotonic()`, and asserts zero Borg exit codes via `get_reset_ec`.
- Nested `test_files(path, count, size, random)` creates temporary benchmark input files using `SyncFile`, all-zero buffers, or `os.urandom`.
- `do_benchmark_cpu(args)` uses `timeit` across chunker specs, crypto hash/MAC functions, encryption modes, compression specs, and msgpack packing.
- `build_parser_benchmarks()` registers `benchmark`, nested `crud`, nested `cpu`, `PATH`, `--json-lines`, and `--json`.

## Control Flow
For CRUD benchmarks, the command selects a test matrix. Normal mode uses six datasets ranging from ten 100 MB files to ten thousand 10 KB files, each with zero and random variants; `_BORG_BENCHMARK_CRUD_TEST` selects tiny CI-friendly cases. For each dataset, it creates temporary input under `args.path`, measures first archive creation with disabled files cache, creates/deletes a second archive to populate cache, measures no-change update, measures dry-run extraction, and measures deletion of the last remaining benchmark archive. Output is plain text throughput or JSON Lines.

For CPU benchmarks, the command selects iteration counts and data size based on `_BORG_BENCHMARK_CPU_TEST`, creates random buffers and keys, times chunkers, hash/MAC functions, authenticated encryption algorithms, compression algorithms/levels, and msgpack packing, then prints human-readable timings or a structured JSON object.

## State and Persistence Behavior
CRUD benchmarking writes temporary input files under the supplied path and creates/deletes archives named `borg-benchmark-crud*` in the supplied repository. It intentionally mutates repository contents and cache state; it suppresses some delete warnings because the repository is expected to be temporary or disposable. CPU benchmarking is in-memory except for normal process memory pressure and imports. Both commands reset Borg global exit-code state after internal command calls.

## Dependencies and Integration Points
The CRUD path integrates tightly with other Archiver methods (`do_create`, `do_delete`, `do_extract`) and relies on normal repository/cache/manifest command decorators. It depends on `SyncFile`, tempfile, logging, constants, and helper format/JSON functions. CPU benchmarking depends on Borg chunkers, crypto low-level extension classes/functions, `blake3`, compression specs, `Item`, and msgpack.

## Risks and Edge Cases
- `benchmark crud` can consume substantial disk space and repository bandwidth; normal datasets need roughly gigabyte-scale input per case plus repository overhead.
- It assumes benchmark archive names are safe to create/delete; running against a valuable existing repository risks name collisions or unwanted churn.
- Direct internal command invocation means parser/command side effects such as global exit-code state and logging must be handled carefully.
- Assertions enforce success; under Python optimized mode assertions would be disabled, but Borg refuses optimized mode in the top-level archiver.
- CPU timings can be noisy and depend heavily on CPU frequency scaling, memory pressure, native extensions, and optional blake3 threading.

## Test Signals
CI should use `_BORG_BENCHMARK_CRUD_TEST` and `_BORG_BENCHMARK_CPU_TEST` to keep runtime bounded. Tests should validate JSON/JSON Lines schema, internal command propagation of `--rsh`/`--remote-path`, no leftover temporary input directories, expected creation/deletion of benchmark archives, and successful CPU benchmark imports. Manual performance runs should be done on idle systems with disposable repositories.
