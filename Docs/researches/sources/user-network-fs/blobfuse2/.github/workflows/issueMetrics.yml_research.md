# sources/user-network-fs/blobfuse2/.github/workflows/issueMetrics.yml

## Purpose
This monthly workflow generates issue and pull-request metrics for the previous 90 days and publishes the report to the `benchmarks` branch.

## Important APIs, Types, and Functions
It uses `actions/checkout@v6`, `actions/setup-python@v6`, `PyGithub`, and repository script `scripts/issueMetrics.py --days 90`. It writes `issueMetric.txt` and date-stamped files under `issueMetrics/`.

## Control Flow
On manual dispatch or the first day of each month, it checks out main, installs Python dependencies, runs the metrics script with `GH_TOKEN` and `REPO_NAME`, checks out the `benchmarks` branch into `benchmarks-branch`, copies the generated report into current and archival paths, commits if there are changes, and pushes to `benchmarks`.

## State and Persistence Behavior
Persistent state is the `benchmarks` branch report file and dated history files. The workflow mutates git config and branch contents in the secondary checkout.

## Dependencies and Integration Points
It integrates GitHub repository issue/PR data with the project's benchmark/reporting branch. It depends on `scripts/issueMetrics.py` and GitHub token access.

## Risks and Edge Cases
The `contents: write` permission allows branch mutation. If the `benchmarks` branch is missing or diverged, the checkout/push path fails. Metrics quality depends on API pagination and rate limits inside the script.

## Test Signals
Signals include successful report generation, a no-op commit path when unchanged, and a dated `issueMetrics/issueMetric-YYYY-MM-DD.txt` file on `benchmarks`.
