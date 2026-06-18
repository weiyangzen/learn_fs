# sources/storage-engines/rocksdb/buckifier/targets_builder.py research

Purpose: `targets_builder.py` is the imperative writer used by RocksDB's buckifier flow to emit a generated Buck `TARGETS` file. It wraps string templates from `targets_cfg.py`, normalizes list formatting, and appends Buck macro invocations for libraries, RocksDB libraries, binaries, tests, benches, exported files, and oncall ownership.

Important APIs: `LiteralValue` marks values that must be emitted without quoting. `smart_quote_value()` and `pretty_list()` convert Python lists into deterministic Buck list fragments, sorting multi-item lists. `TARGETSBuilder.__init__()` creates/truncates the output file and writes the generated-file header. Builder methods include `add_oncall()`, `add_library()`, `add_rocksdb_library()`, `add_binary()`, `add_c_test()`, `add_test_header()`, `add_fancy_bench_config()`, `register_test()`, and `export_file()`.

Control flow: callers construct `TARGETSBuilder(path, extra_argv)` once and call append methods in generation order. Each method opens the same file in append mode, formats a template with normalized arguments, writes bytes or text, and updates simple counters for libraries, binaries, and tests.

State and persistence: persistent state is the generated file at `self.path`; in-memory state is limited to `total_lib`, `total_bin`, `total_test`, and an unused `tests_cfg` string. The output is not transactional beyond the initial truncating header write.

Dependencies and integration: the file imports `targets_cfg` template constants and `pprint` for bench configuration rendering. It is designed for the Meta-specific `buckifier/buckify_rocksdb.py` pipeline and generated Buck macros loaded by the header template.

Risks and test signals: generated syntax depends on template correctness and manual quoting rules. Sorting `pretty_list()` makes output stable but changes caller ordering. `LiteralValue` bypasses quotes, so unsafe input can inject arbitrary Buck expressions. Test signals are generated-file diffs, Buck parser failures, and successful Buck builds/tests consuming the generated `TARGETS`.
