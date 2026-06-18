# sources/storage-engines/pebble/.github/actions/post-issue/action.yaml

## Purpose
This composite GitHub Action creates a new issue or comments on an existing issue with a matching title, giving nightly workflows a reusable failure-reporting primitive.

## Important APIs, types, and functions
Inputs include `token`, `title`, `body`, optional `unique-title-includes`, and optional `labels`. It uses `actions-cool/issues-helper@v3` for issue search, creation, and comments. A bash step with `jq` extracts the first matching issue number. The action exposes output `issue-number`.

## Control flow
The action searches for issues whose title includes the unique string or title. If a number is found, it records that number in `GITHUB_OUTPUT`; otherwise it creates a new issue. A conditional comment step runs for existing issues. The final step normalizes either found or created issue number into the action output.

## State and persistence behavior
The action mutates GitHub issue state by creating issues or comments. It stores only transient step outputs inside the workflow run.

## Dependencies and integration points
Nightly Pebble workflows call this action on failure. It depends on GitHub token permissions, `jq` availability on the runner, and the third-party `actions-cool/issues-helper` action.

## Risks and edge cases
The title matching is broad and may comment on an unrelated issue if titles overlap. Pulling issue JSON into a heredoc from an action output must remain valid shell/JQ input. Third-party action behavior and permissions are supply-chain and reliability dependencies.

## Test signals
Validation should cover no existing issue, one matching issue, multiple matches, custom unique-title strings, label assignment, and token permission failures.
