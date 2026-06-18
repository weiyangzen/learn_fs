<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_ci_commit_message.sh -->
# sources/test-tools/kdevops/scripts/generate_ci_commit_message.sh

Purpose: builds a structured commit message for kdevops CI results archives. It formats either kdevops validation or Linux test-suite results with build metadata, execution results, and machine-readable metadata.

Important APIs and functions: `wrap_commit_subject()` folds long subjects; `calculate_duration()` uses `ci.start_time`; `determine_scope()` chooses `kdevops` or `tests` from `TEST_MODE`; `get_kernel_info()` reads the `linux` repo; `get_kdevops_info()` reads current repo; `get_test_results()` reads result files; `get_workflow_type()` classifies workflow names; `generate_commit_message()` assembles heredoc output; `main()` validates `CI_WORKFLOW`.

Control flow: environment defaults are initialized, metadata files are read when present, git state is queried, result content is loaded, a header is selected based on scope/status, and the formatted message is printed to stdout.

State and persistence: read-only; consumes CI metadata files such as `ci.commit_extra`, `ci.result`, `ci.ref`, and `ci.trigger`.

Dependencies and integration: bash with `set -euo pipefail`, git, date, fold, sed, cut. It is intended for GitHub Actions or archive automation.

Risks: pipe-delimited parsing of git subjects can break if subjects contain `|`. The required `CI_WORKFLOW` check is ineffective because a default is assigned. A Unicode arrow appears in one line, which may matter in strict ASCII logs. Test signals include fixture repos, all workflow-type branches, missing metadata files, pass/fail result values, long subject wrapping, and `TEST_MODE=kdevops-ci` formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_ci_commit_message.sh -->
