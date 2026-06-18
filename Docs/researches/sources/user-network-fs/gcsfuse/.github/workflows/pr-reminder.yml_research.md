## sources/user-network-fs/gcsfuse/.github/workflows/pr-reminder.yml

Purpose: Scheduled/manual workflow that runs the PR reminder script.

Important APIs/types/functions: triggers on `workflow_dispatch` and weekday hourly cron from 03:30 to 11:30 UTC. The `remind` job grants `pull-requests: write` and `issues: write`, checks out code, sets up Node 20, installs `@actions/github@5.1.1 @actions/core`, and runs `.github/scripts/reminder.js` with `GITHUB_TOKEN`.

Control flow: each scheduled tick runs dependency install then script execution over open PRs.

State and persistence: creates PR comments through `reminder.js`.

Dependencies and integration points: pairs with `auto-pr-reminder.yml` for label creation and uses GitHub's default token.

Risks: unpinned npm transitive dependencies can vary despite top-level pin. Scheduled comments may repeat if labels remain and PRs stay inactive. Job has write permissions but only runs repository code on scheduled/manual events.

Test signals: workflow logs and resulting comments on eligible PRs.
