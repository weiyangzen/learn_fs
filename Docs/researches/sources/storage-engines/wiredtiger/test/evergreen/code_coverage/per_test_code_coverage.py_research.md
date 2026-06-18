<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/per_test_code_coverage.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage/per_test_code_coverage.py

Purpose: captures coverage separately for each configured test command by running tests in copied build directories, copying each completed build directory, and optionally running gcovr over every copy.

Important APIs: `delete_runtime_coverage_files()` removes `.gcda` files before each task. `run_coverage_task(index, task)` sets GCOV remapping, deletes old runtime coverage, executes the test, copies the build dir to `build_N_copy`, and writes `task_info.json`. `run_gcovr(build_dir_base, gcovr_dir)` scans sibling build copies, creates one output directory per copy, copies task info, and runs gcovr with HTML, summary JSON, and full JSON outputs.

Control flow: `main()` validates arguments, enforces absolute `gcovr_dir`, loads config, sets up or checks build dirs, dispatches all test tasks through the shared process pool, and then runs gcovr when requested.

State and persistence: creates many full build directory copies and gcovr report directories. This is intentionally high-disk-use and later packed by wrapper scripts.

Dependencies and integration: used by `coverage-report-per-test.sh`; output is consumed by `per_test_code_coverage_report.py`.

Risks and test signals: failed test commands are printed but not necessarily fatal unless future exception behavior is triggered; `CalledProcessError` is swallowed in `run_coverage_task`. Copy names depend on task index and can be large. `task.split()` limits commands with quoted arguments.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/per_test_code_coverage.py -->
