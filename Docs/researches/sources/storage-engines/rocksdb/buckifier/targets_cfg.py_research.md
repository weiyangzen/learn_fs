# sources/storage-engines/rocksdb/buckifier/targets_cfg.py research

Purpose: `targets_cfg.py` is a template-only companion to the RocksDB buckifier. It centralizes generated Buck syntax snippets used by `targets_builder.py`, including the file header, load statements, and macro call bodies for libraries, binaries, tests, benches, exports, and oncall metadata.

Important APIs: the module exposes constants rather than functions: `rocksdb_target_header_template`, `library_template`, `rocksdb_library_template`, `binary_template`, `unittests_template`, `fancy_bench_template`, `export_file_template`, and `oncall_template`. These constants are Python `str.format()` templates whose placeholders must match the arguments supplied by `TARGETSBuilder`.

Control flow: there is no runtime control flow beyond module import. The builder imports these strings and formats them during generation. The header template records the invoking buckifier command and loads wrapper macros from `//rocks/buckifier:defs.bzl` plus `export_file`.

State and persistence: the module is stateless and does not write files. Persistent output is produced only by consumers that format these templates into `TARGETS`.

Dependencies and integration: template bodies assume Buck/Starlark macro names such as `cpp_library_wrapper`, `rocks_cpp_library_wrapper`, `cpp_binary_wrapper`, `cpp_unittest_wrapper`, `fancy_bench_wrapper`, and `add_c_test_wrapper`. The header explicitly describes the generated file as Meta-specific and not generally validated outside Meta.

Risks and test signals: placeholder drift between `targets_cfg.py` and `targets_builder.py` will fail at generation time with `KeyError` or produce malformed Buck code. Some builder arguments, such as `extra_external_deps`, are accepted by builder APIs but not represented in the current template, which is a maintenance signal. Tests should compare generated `TARGETS` snapshots and run Buck parsing/build validation in the Meta environment.
