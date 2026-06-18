# sources/storage-engines/wiredtiger/.github/workflows/pr_title_checker.yml

## Purpose
This workflow enforces WiredTiger PR title policy on opened, edited, and synchronized pull requests.

## Important APIs, Types, and Functions
It runs `thehanimo/pr-title-checker@v1.4.3` with `GITHUB_TOKEN`, `pass_on_octokit_error: false`, and a configuration file path `.github/workflows/pr_title_checker_config.json`.

## Control Flow, State, and Dependencies
Each trigger starts a single `ubuntu-latest` job. The action reads the JSON config and fails the job if the title does not match policy. No repository state is modified.

## Integration Points, Risks, and Test Signals
It integrates with GitHub branch protection/status checks. Risks are third-party action availability and config regex mistakes. Signal is pass/fail status on the PR.
