<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/__init__.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/runner/__init__.py

Purpose: package initializer for Workgen runner scripts. It discovers a usable WiredTiger build, sets Python/library paths when necessary, imports `wiredtiger` and `workgen`, and re-exports runner helper APIs.

Important APIs and functions: `_prepend_env_path(pathvar, s)` prepends library directories. Module-level logic computes `thisdir`, `workgen_src`, `wt_dir`, `curdir`, and `wt_builddir`; may re-exec Python with `_workgen_init` set to refresh dynamic library search paths. Exports `txn`, `extensions_config`, `op_append`, `op_group_transaction`, `op_log_like`, `op_multi_table`, `op_populate_with_range`, `sleep`, `timed`, `workload_latency`, and `get_cache_eviction_stats`.

Control flow: prefer `WT_BUILDDIR`; else current directory containing `wt`; else warn. Try importing `wiredtiger`; on failure add source/build Python paths; on continued failure set `LD_LIBRARY_PATH`/`DYLD_LIBRARY_PATH` and `os.execv` the interpreter once. Then similarly import `workgen` after adding source/build paths if needed.

State and persistence: mutates `os.environ`, `sys.path`, and potentially replaces the running process. No disk writes except downstream imports.

Dependencies and integration: every runner script imports this package first, allowing direct execution without manual environment setup.

Risks: re-exec can surprise debuggers and wrappers. Path detection can choose the wrong build in multi-build trees. Bare `except` blocks hide import details. If re-exec fails, the user gets guidance but execution exits.

Test signals: successful import of `runner`, `wiredtiger`, and `workgen`; warning messages when build discovery fails.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/__init__.py -->
