# sources/storage-engines/wiredtiger/.github/workflows/pr_title_checker_config.json

## Purpose
This JSON file configures the PR title checker workflow. It requires titles to start with a WiredTiger ticket number or a `Revert "` prefix followed by a ticket.

## Important APIs, Types, and Functions
`CHECKS.regexp` is `^(Revert \")?WT-[0-9]+ [ -~]+$`, constraining titles to `WT-<digits> ` plus printable ASCII. `MESSAGES` define success and failure text.

## Control Flow, State, and Dependencies
The file is read by `thehanimo/pr-title-checker`; it has no independent execution. Policy state is versioned in the repository.

## Integration Points, Risks, and Test Signals
It integrates with `.github/workflows/pr_title_checker.yml`. Risk is rejecting valid non-ASCII titles or non-WT maintenance PRs. Signal is the title-check workflow result.
