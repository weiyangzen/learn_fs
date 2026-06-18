<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/cyclomatic-complexity.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/cyclomatic-complexity.sh

Purpose: collects cyclomatic complexity metrics, enforces high-complexity gates, and writes Atlas-compatible complexity statistics.

Control flow: sources `download_metrixpp.sh`, creates `code_statistics_report`, enters `src`, runs Metrix++ collect/view, reports all functions above complexity 20, then fails if any function exceeds 98 by redirecting Metrix++ limit output to `$t` and grepping for `exceeds`. It writes a Python-format summary JSON and CSV export, creates a virtualenv, installs pandas, and runs `code_complexity_analysis.py`.

State and persistence: creates Metrix++ db under `src`, `code_statistics_report/code_complexity_summary.json`, `metrixpp.csv`, and `atlas_out_code_complexity.json`.

Dependencies and integration: Evergreen `cyclomatic-complexity` task. Depends on Metrix++ pinned clone, Python, pandas, and exact Metrix++ output shape.

Risks and test signals: `$t` is not initialized in the script, so it relies on environment or shell behavior and may fail unexpectedly. Complexity threshold failure is explicit with `[ERROR]` log lines. Running from the wrong repo root breaks relative paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/cyclomatic-complexity.sh -->
