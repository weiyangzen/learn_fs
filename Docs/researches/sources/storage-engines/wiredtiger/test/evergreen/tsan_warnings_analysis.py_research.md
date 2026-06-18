<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/tsan_warnings_analysis.py -->
# sources/storage-engines/wiredtiger/test/evergreen/tsan_warnings_analysis.py

Purpose: scans TSAN log files, deduplicates warnings by normalized summary, optionally filters to warnings touching recently modified lines, and fails the task when warnings remain.

Important APIs: `get_tsan_warnings()` recursively finds files whose names start with `tsan_logs`, records lines from `WARNING:` through `SUMMARY:`, normalizes summary paths by stripping up to `wiredtiger/` and removing column numbers, and maps summary to `(log_name, warning_lines)`. `get_line_last_modified_times(file_path, line_number)` runs `git blame --line-porcelain` and extracts `author-time`.

Control flow: `main()` parses optional timestamp. When provided, it keeps only warnings whose parsed data-race file/line blame time is at or after the filter timestamp, or warnings it cannot parse. It prints all remaining warning blocks and exits 1, otherwise prints no warnings.

State and persistence: reads TSAN logs and Git history; writes only stdout.

Dependencies and integration: Evergreen TSAN analysis task after sanitizer runs. Depends on TSAN `log_path` naming, summary format, and Git blame availability.

Risks and test signals: only summaries matching `data race (.*):(\d+)` are timestamp-filtered. Deduplication by summary can collapse separate occurrences. `exit(1)` is used in one helper instead of `sys.exit`. Non-data-race TSAN reports are retained when unparseable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/tsan_warnings_analysis.py -->
