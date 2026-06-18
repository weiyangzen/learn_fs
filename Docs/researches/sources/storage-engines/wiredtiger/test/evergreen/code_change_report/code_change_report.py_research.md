<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_report.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_report.py

Purpose: renders `code_change_info.py` JSON into an HTML report and optionally maintains a sticky GitHub PR comment summarizing changed-code coverage and complexity warnings.

Important APIs: report helpers colorize line/branch coverage (`get_html_color`, `get_coverage_html_color`), complexity (`get_complexity_html_color`), and deltas (`change_string`). `generate_summary_table()`, `generate_changed_function_table()`, `generate_file_info_as_html_text()`, and `generate_html_report_as_text()` build HTML as lists of strings. `build_pr_comment()` creates markdown with line/branch coverage links and high-complexity warnings. `post_pr_comment()` searches issue comments for a magic marker, then creates, updates, or deletes it.

Control flow: `main()` parses input JSON, output HTML, optional report URL, GitHub repo/PR/token, and verbose flag. It writes HTML unconditionally and posts comments only when both PR number and token are present.

State and persistence: writes the HTML report, uses GitHub issue comment state when enabled, and reads no repository state directly.

Dependencies and integration: consumes the exact JSON contract from `code_change_info.py`; `coverage-report.sh` builds the URL and PR arguments. Uses `requests` and GitHub REST API.

Risks and test signals: HTML is assembled manually, so structural mistakes are possible. Only `src/` files receive detailed line tables. Existing sticky comment lookup assumes the marker appears in an early page of comments. Coverage URL derivation uses string replacement of Evergreen task and file names.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_report.py -->
