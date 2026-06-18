<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_info.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_info.py

Purpose: creates the JSON input for the HTML code-change report by joining Git diff hunks, gcovr full JSON coverage, and current/previous Metrix++ complexity CSVs.

Important APIs: `read_coverage_data`, `get_git_diff`, `find_file_in_coverage_data`, `find_line_data`, `find_line_coverage`, and `find_covered_branches` query gcovr data. `get_function_coverage()` counts executable lines and branches in a function range, while `get_function_info()` locates the function containing a changed line and adds complexity, line count, coverage, and previous-version metrics. `create_report_info()` produces `summary_info`, `change_info_list`, and `changed_functions`.

Control flow: `main()` parses coverage, complexity, previous complexity, git root, optional diff file, output, and verbose flags. It reads coverage/CSV inputs, gets a pygit2 diff either from repository HEAD versus parent or from `Diff.parse_diff()`, converts hunks, creates the report object, and writes pretty JSON.

State and persistence: reads repository metadata and report inputs; writes only the output JSON. Summary counters count added/changed useful lines where `old_lineno < 0`.

Dependencies and integration: used by `coverage-report.sh`; depends on pygit2, gcovr JSON schema, Metrix++ CSV columns, and local helpers.

Risks and test signals: HEAD must have a parent when no diff file is supplied. Diff parse failures fall back to an empty diff. Function lookup is line-range based and duplicate function names can collapse. Branch counts assume non-negative gcovr counts except later HTML code handles negative branch counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_info.py -->
