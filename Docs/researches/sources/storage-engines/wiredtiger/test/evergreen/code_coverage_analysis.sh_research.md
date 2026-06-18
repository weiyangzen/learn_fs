<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage_analysis.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage_analysis.sh

Purpose: Evergreen shell wrapper around gcovr and `code_coverage_analysis.py` for full or combined coverage reports.

Control flow: validates at least coverage filter, job count, and Python binary; if `combine_coverage_report` is `True`, requires two tracefile paths. It creates a Python virtualenv, installs gcovr dependencies, creates `coverage_report`, defines gcovr output flags for self-contained HTML details, summary JSON, and full JSON. In combine mode it runs gcovr with two `--add-tracefile` inputs. Otherwise it scans local coverage files with `-f $coverage_filter`, then runs the Python analyzer with timing data. If `generate_atlas_format` is non-empty, it writes component coverage Atlas JSON.

State and persistence: writes virtualenv and coverage report outputs. Reads optional `time.txt` and tracefile inputs.

Dependencies and integration: invoked by Evergreen coverage report tasks. Requires gcovr 5.0 and a build tree with `.gcno/.gcda` files or supplied tracefiles.

Risks and test signals: tests for non-empty strings use unquoted variables (`[ ! -z $combine_coverage_report ]`), so unset/empty values can behave unexpectedly. Combine mode skips the timing/rate print. Success depends on gcovr exit status and analyzer schema compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage_analysis.sh -->
