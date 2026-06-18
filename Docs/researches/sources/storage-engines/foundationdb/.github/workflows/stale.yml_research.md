# sources/storage-engines/foundationdb/.github/workflows/stale.yml

## Purpose
This GitHub Actions workflow marks and closes stale pull requests.

## Important APIs, Types, And Functions
It runs `actions/stale` v10.2.0 pinned by SHA on a daily cron at 20:15 UTC. Permissions allow actions, issues, and pull-request writes. Configuration marks PRs stale after 150 inactive days, closes 14 days later, effectively disables issue staleness with 5475 days, processes 80 operations per run, and handles oldest items first.

## Control Flow
The scheduled job invokes the stale action with the configured message and thresholds.

## State And Persistence Behavior
It mutates GitHub PR labels/comments and may close PRs. It does not touch repository files.

## Dependencies And Integration Points
It integrates with GitHub Actions scheduling and the marketplace stale action.

## Risks And Edge Cases
Long-lived but intentionally open PRs can be closed if maintainers miss the label/comment window. Operation limits can delay processing large backlogs.

## Test Signals
Operational signals are action logs, applied stale labels, comments, and PR closures.
