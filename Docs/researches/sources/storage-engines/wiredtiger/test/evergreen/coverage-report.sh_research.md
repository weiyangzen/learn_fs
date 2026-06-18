<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/coverage-report.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/coverage-report.sh

Purpose: generates the changed-code coverage/complexity HTML report after full coverage data is available.

Control flow: accepts `is_patch`, Python binary, GitHub commit, and optional PR args. It creates a virtualenv and installs pygit2/requests. For patch builds it runs `git_diff_tool.py`, writes `diff.txt` and `diff.html`, and passes `-d` to code-change info generation. It downloads Metrix++, collects current complexity from `src`, then creates a detached `wiredtiger_previous` worktree at `github_commit`, checks out either the branch point from develop for patches or `HEAD~` for non-patches, and collects previous complexity. Finally it runs `code_change_info.py`, logs JSON, and runs `code_change_report.py`.

State and persistence: writes virtualenv, Metrix++ checkout/db, `coverage_report/metrixpp*.csv`, diff files, `code_change_info.json`, `code_change_report.html`, and a Git worktree.

Dependencies and integration: Evergreen `code-change-report` task consumes coverage artifacts and uses this wrapper. Depends on `coverage_report/full_coverage_report.json`, git, Metrix++, pygit2, and optional GitHub PR token args.

Risks and test signals: worktree cleanup is not handled here. Patch branch-point logic depends on `dist/common_functions.py last_commit_from_dev`. The script assumes `src` exists and coverage paths align with complexity paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/coverage-report.sh -->
