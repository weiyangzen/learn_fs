<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/issueMetrics.py -->
# sources/user-network-fs/blobfuse2/scripts/issueMetrics.py

## Purpose
Generates terminal reports for recent GitHub issue and PR activity, including counts, resolution times, first-comment times, author ownership, and Copilot-tagged activity.

## Important APIs, Types, and Functions
`get_env_var`, `get_gh_cli_token`, and `get_gh_cli_repo` discover credentials and repo. `parse_args` supports `--days`, `--only-copilot-tagged`, and `--summary`. `print_table` renders fixed-width tables. Formatting helpers convert durations and truncate titles. `is_copilot_tagged` inspects labels. `get_first_comment_time_display_for_pr` checks issue and review comments. `main` authenticates via PyGithub, scans issues and PRs, computes metrics, and prints tables.

## Control Flow and State
The script chooses token from env or `gh auth`, chooses repo from env or `gh repo view`, validates inputs, then fetches data since a UTC lookback timestamp. It skips PRs in the issue loop, filters PRs to base branch `main`, and breaks PR iteration once created dates are older than the window.

## Dependencies and Integration Points
Depends on `PyGithub`, `gh` CLI optionally, GitHub API access, and standard Python libraries. It is a local/reporting utility for maintainers.

## Risks and Edge Cases
API iteration can be slow and rate-limited. PR first-comment retrieval handles exceptions by returning `Unavailable`. Copilot detection is heuristic: labels containing copilot, author `dependabot[bot]`, or author `copilot`. The PR loop assumes created-date descending order and base branch `main`.

## Test Signals
Exit code `0` and printed tables signal success. Error messages cover missing token, missing repo, bad credentials, bad repo access, and invalid day count.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/scripts/issueMetrics.py -->
