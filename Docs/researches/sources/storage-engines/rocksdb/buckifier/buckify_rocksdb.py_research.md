# sources/storage-engines/rocksdb/buckifier/buckify_rocksdb.py

## Purpose

`buckify_rocksdb.py` is the RocksDB Buck target generator. It reads RocksDB source manifests and benchmark configs, discovers source/test files, and rewrites the repository `BUCK` file through `TARGETSBuilder`.

It is intended to be run from the RocksDB checkout as:

- `python3 buckifier/buckify_rocksdb.py`
- `python3 buckifier/buckify_rocksdb.py '<json dependency map>'`

The optional JSON argument lets callers generate variant test targets with extra dependencies and compiler flags.

## Important APIs, Functions, and Data

- `_EXPORTED_TEST_LIBS = ["env_basic_test"]`: tests that get a dedicated library target before registration, allowing inclusion by other projects.
- `parse_src_mk(repo_path)`: reads `src.mk` and returns a map from make variable name to listed `.c`/`.cc` paths. It treats lines containing `=` as variable starts and lines containing `.c` as file entries.
- `get_cc_files(repo_path)`: recursively discovers `.cc` and `.c` files, skipping roots containing `java`. In this version, the collected list is assigned but not used for target generation.
- `get_non_parallel_tests(repo_path)`: parses `NON_PARALLEL_TEST =` from `Makefile` into a set. In this version, the result is collected but not used when registering tests.
- `get_dependencies()`: returns a default dependency map for the empty target alias, optionally extended from `sys.argv[1]` JSON. Each entry is expected to contain `extra_deps` and `extra_compiler_flags`.
- `generate_buck(repo_path, deps_map)`: main generator that writes libraries, binaries, benchmarks, tests, and exported files.
- `get_rocksdb_path()`: derives the repository path as the parent of the directory containing `sys.argv[0]`.
- `exit_with_error(msg)`: prints an error using `ColorString.error` and exits nonzero.
- `main()`: parses dependency config and runs generation.

The generator depends on `TARGETSBuilder` and `LiteralValue` from `targets_builder.py`, and `ColorString` from `util.py`.

## Control Flow

`main()` calls `get_dependencies()`, computes the RocksDB path, and calls `generate_buck()`.

Inside `generate_buck()`:

1. Print an informational message.
2. Parse `src.mk` into source groups.
3. Discover all C/C++ files and non-parallel tests, though these two data sets are not currently used later.
4. Build `extra_argv` from the optional dependency-map argument for inclusion in the generated file header.
5. Instantiate `TARGETSBuilder("%s/BUCK" % repo_path, extra_argv)`, which immediately truncates and rewrites `BUCK`.
6. Add the oncall marker.
7. Add core library targets:
   - `rocksdb_lib` from `LIB_SOURCES`, `RANGE_TREE_SOURCES`, and `TOOL_LIB_SOURCES`, with header glob and Folly dependencies.
   - `rocksdb_whole_archive_lib` with `link_whole=True`.
   - `rocksdb_with_faiss_lib`.
   - `rocksdb_test_lib`.
   - `rocksdb_with_faiss_test_lib`.
   - `rocksdb_tools_lib`.
   - `rocksdb_cache_bench_tools_lib`.
   - `rocksdb_point_lock_bench_tools_lib`.
   - `rocksdb_stress_lib`.
8. Add binaries:
   - `ldb`
   - `db_stress`
   - `db_bench`
   - `cache_bench`
   - `point_lock_bench`
   - one binary per `MICROBENCH_SOURCES` entry.
9. Validate C test handling: only `db/c_test.c` is supported in `TEST_MAIN_SOURCES_C`; any other C test returns failure.
10. Add the C test wrapper.
11. Try to load `bench.json` and `bench-slow.json`, clean metric lists by removing dict entries, and add fancy-bench configs.
12. Add a generated test section header.
13. Build `test_source_map` from `TEST_MAIN_SOURCES` and `WITH_FAISS_TEST_MAIN_SOURCES`.
14. For each dependency alias and sorted test source, register a test target. Alias variants append `_<alias>` to the target name.
15. For `env_basic_test`, add a dedicated test library and register the test against that library.
16. FAISS tests depend on `:rocksdb_with_faiss_test_lib`; other tests depend on `:rocksdb_test_lib`.
17. Export `tools/db_crashtest.py`.
18. Print generated target counts and return success.

## State and Persistence Behavior

This script rewrites `BUCK` in place. `TARGETSBuilder.__init__` opens the file in binary write mode, so generation starts by truncating any existing `BUCK`. Subsequent builder calls append target stanzas. If generation fails after builder creation, a partial `BUCK` can remain unless the caller, such as `check_buck_targets.sh`, made a backup.

The optional command-line dependency JSON is not persisted separately; it is embedded in the generated header as canonicalized extra argv text and affects generated test target names, dependencies, and compiler flags.

No caches or databases are maintained. All state comes from the repository files (`src.mk`, `Makefile`, benchmark JSON files) and is materialized as generated `BUCK`.

## Dependencies and Integration Points

Source manifests:

- `src.mk`: authoritative source-group manifest for libraries, tests, tools, benchmarks, and optional FAISS sources.
- `Makefile`: source for `NON_PARALLEL_TEST`, although this data is currently unused.

Generator modules:

- `targets_builder.py`: concrete API for appending target stanzas.
- `targets_cfg.py`: templates and Buck macro loads used by the builder.
- `util.py`: colored status output.

Build-system integration:

- Emits Buck macros such as C++ libraries, binaries, unit tests, C test wrapper, fancy bench wrapper, and export file wrapper.
- Hard-codes dependencies on internal targets such as Folly coroutine/container/synchronization libraries and FAISS.
- Reads `bench.json` and `bench-slow.json` to emit fancy-bench configs.
- Used by `check_buck_targets.sh` as the source of truth for whether committed `BUCK` is fresh.

## Risks and Edge Cases

- `BUCK` is truncated at builder construction. Any exception after that point can leave a partial generated file when not wrapped by a backup/restore script.
- `parse_src_mk()` is a simple line parser. It assumes source entries contain `.c`, variable assignments contain `=`, and continuation/file syntax follows the existing `src.mk` pattern.
- `get_cc_files()` and `get_non_parallel_tests()` are computed but unused, which can mislead maintainers into thinking discovery or non-parallel behavior affects generated targets.
- `get_dependencies()` trusts the optional JSON shape. Missing `extra_deps` or `extra_compiler_flags` keys will fail later during test registration.
- The broad benchmark `try/except Exception: pass` hides malformed JSON, missing keys, template failures, or file IO issues. The generator can succeed while silently omitting fancy-bench targets.
- Slow benchmark config generation appears to reuse the final `clean_benchmarks` value for every slow suite because cleaning and emission happen in separate loops. This likely makes every `_slow` generated target use the last slow suite's benchmark map.
- Only `db/c_test.c` is supported in `TEST_MAIN_SOURCES_C`; adding another C test causes generation failure.
- Test target aliases are built by string concatenation (`test + "_" + target_alias`), so aliases should be Buck-name-safe.
- `get_rocksdb_path()` uses `sys.argv[0]`; unusual invocation paths can point generation at the wrong parent directory.

## Test Signals

Primary test signal is deterministic regeneration:

- `buckifier/check_buck_targets.sh` backs up `BUCK`, runs this script, checks `git diff BUCK`, restores the backup, and fails if regeneration changes `BUCK`.

Additional signals:

- Running the script should print generated counts for libraries, binaries, and tests.
- `jq` validation of `bench.json` and `bench-slow.json` helps isolate benchmark parse failures that the script would otherwise swallow.
- A useful regression test would assert that slow fancy-bench configs preserve each suite's own benchmark map instead of all sharing the last map.
