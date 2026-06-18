<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/per_test_code_coverage_report.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_change_report/per_test_code_coverage_report.py

Purpose: correlates changed functions with per-test gcovr outputs to identify which test commands reached each changed function. It is a diagnostic companion to the full code-change report.

Important APIs: `collate_coverage_data(gcovr_dir)` scans build copy directories, reads `task_info.json` and `full_coverage_report.json`, and indexes by task command. `get_function_info()` maps changed line numbers to Metrix++ function ranges. `create_report_info()` extracts changed functions from a pygit2 diff. `get_function_coverage()` checks each test's file/line counts for any covered line within the function range. `generate_report()` logs changed files/functions and reached-by-test lines.

Control flow: `main()` parses coverage data directory, diff file, complexity CSV, and verbose flag. It parses the diff, reads/preprocesses complexity data, collates coverage JSON, and logs the reachability report.

State and persistence: reads many JSON reports from per-test build copies; writes no report file itself. Output is logging/stdout.

Dependencies and integration: invoked by `code_coverage/coverage-report-per-test.sh` after per-test coverage generation. Depends on gcovr full JSON schema, `task_info.json`, pygit2 diff parsing, and Metrix++ CSV columns.

Risks and test signals: memory use can be large because all coverage JSON is loaded. Build copy names are selected by `build_*copy`. Failed tests may still produce partial coverage but missing JSON will fail reads. The function coverage result is logged only in verbose/debug mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/per_test_code_coverage_report.py -->
