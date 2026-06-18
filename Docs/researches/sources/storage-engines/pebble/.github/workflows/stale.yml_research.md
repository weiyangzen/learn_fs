# sources/storage-engines/pebble/.github/workflows/stale.yml

## Purpose
`stale.yml` automatically marks inactive issues stale and eventually closes them, while effectively disabling stale handling for pull requests.

## Important APIs, types, and functions
It runs `actions/stale@v3` on a Monday-Thursday schedule and manual dispatch. Configuration sets operation limits, messages, labels, close labels, `days-before-issue-stale: 540`, `days-before-close: 10`, `days-before-pr-stale: 99999`, and exempt issue label `X-nostale`.

## Control flow
The single job grants issue and pull-request write permissions, then runs the stale action with repo token and policy settings. Inactive issues receive `no-issue-activity`, then `X-stale` on close after the grace period. PR stale timing is set high enough to avoid normal PR stale closure.

## State and persistence behavior
It mutates GitHub issue/PR labels and may close issues. It does not touch repository files.

## Dependencies and integration points
The workflow integrates repository triage policy with GitHub Issues and depends on the third-party stale action.

## Risks and edge cases
Older `actions/stale@v3` behavior may diverge from current GitHub APIs. Broad operation limits can label many issues in one run. Incorrect exempt labels or messages can close still-relevant issues.

## Test signals
Manual dry runs on a test repository or limited labels should confirm stale labeling, exemption behavior, and close timing.
