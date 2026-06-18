<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/parallel_code_coverage.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage/parallel_code_coverage.py

Purpose: runs coverage test commands in parallel across copied build directories, optionally setting up those directories and optionally rewriting the task list by observed runtime.

Important APIs: `run_task(index, task)` sets `GCOV_PREFIX_STRIP` and `GCOV_PREFIX` for copied-build gcov output remapping, runs the task with stdout/stderr suppressed, exits on failure, and returns timing data. `main()` validates bucket and parallel arguments, loads config JSON, builds or checks build dirs, filters `test_tasks` by `python` or `other`, dispatches through `run_task_lists_in_parallel()`, and in optimize mode sorts tasks by descending runtime and rewrites the config.

State and persistence: setup mode creates build directories via shared utilities. Runtime produces `.gcda` files in per-worker build dirs. Optimize mode mutates the JSON config file.

Dependencies and integration: used by Evergreen split coverage tasks (`coverage-report-python` and `coverage-report-other`). Depends on `code_coverage_utils.py`, gcov cross-profiling environment variables, and command strings that can be safely split.

Risks and test signals: bucket detection is a regex search for `"python"` anywhere in the command. `sys.exit()` inside process workers reports failures through futures only when `--check_errors` is used. Mutating config in optimize mode should not be combined with bucketed subsets, and the script enforces that.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/parallel_code_coverage.py -->
