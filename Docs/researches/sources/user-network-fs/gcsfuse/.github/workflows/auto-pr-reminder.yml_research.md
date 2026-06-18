## sources/user-network-fs/gcsfuse/.github/workflows/auto-pr-reminder.yml

Purpose: Automatically adds the `remind-reviewers` label to eligible PRs.

Important APIs/types/functions: workflow triggers on PR `opened`, `reopened`, and `ready_for_review` against `master`. Single `add-label` job runs only for non-draft PRs, grants `pull-requests: write` and `issues: write`, and uses `actions/github-script@v6`.

Control flow: read PR author, skip excluded authors currently containing `dependabot[bot]`, then call `github.rest.issues.addLabels` with `remind-reviewers`.

State and persistence: persists a GitHub issue label on the PR.

Dependencies and integration points: cooperates with `pr-reminder.yml` and `reminder.js`, which only remind PRs carrying this label.

Risks: running on `pull_request` with write permissions is acceptable for labeling but should avoid checking out untrusted code; this workflow does not checkout. Exclusion list must be maintained for other bots. It does not remove the label when a PR returns to draft.

Test signals: PR event logs and label presence on newly opened/reopened/ready non-draft PRs.
