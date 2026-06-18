## sources/user-network-fs/gcsfuse/.github/scripts/reminder.js

Purpose: GitHub Actions script that posts review-reminder comments on inactive PRs.

Important APIs/types/functions: imports `getOctokit` and `context` from `@actions/github`; `run()` configures `REMINDER_LABEL`, `INACTIVITY_HOURS`, and message template; reads `GITHUB_TOKEN`; paginates open PRs; checks label, draft status, inactivity, requested reviewers; posts `issues.createComment`; exits nonzero on error.

Control flow: iterate all open PRs, skip ones without `remind-reviewers`, skip drafts, skip recently updated PRs, skip PRs without requested reviewers, otherwise mention requested reviewers in a comment. Inactivity is 24 hours minus 10 minutes so the prior reminder's update timestamp does not completely mask the next reminder window.

State and persistence: persists comments on PR issues. It does not remove labels or record which PRs it reminded, so repeated scheduled runs can create repeated comments whenever inactivity remains true.

Dependencies and integration points: run by `pr-reminder.yml` after installing `@actions/github@5.1.1` and `@actions/core`; uses the workflow-provided GitHub token and repository context.

Risks: comments themselves update PR activity, so timing behavior depends on GitHub's `updated_at` semantics. It handles only directly requested reviewers, not requested teams. Lack of idempotent marker can produce recurring reminder comments. Permission or token failures stop the whole workflow.

Test signals: can be tested with a dry-run fork or mocked Octokit; production signal is scheduled workflow logs and reminder comments only on labeled, inactive, non-draft PRs with requested reviewers.
