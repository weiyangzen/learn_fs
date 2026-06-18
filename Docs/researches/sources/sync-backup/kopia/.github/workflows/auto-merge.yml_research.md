# sources/sync-backup/kopia/.github/workflows/auto-merge.yml

Purpose: GitHub Actions workflow that runs Dependabot auto-merge automation on pull requests.

Important APIs/types/functions: workflow `auto-merge`, `pull_request` trigger, checkout action pinned by SHA, `ahmadnassri/action-dependabot-auto-merge` pinned by SHA, and `AUTO_MERGE_TOKEN` secret.

Control flow: on PR events, checkout repository and run action using rules from `.github/auto-merge.yml`.

State and persistence: no repo runtime state; may approve/merge PRs through GitHub API.

Dependencies and integration points: depends on secret availability and auto-merge policy file.

Risks: token scope controls blast radius; pinned action versions must be maintained.

Test signals: workflow run results on Dependabot PRs.
