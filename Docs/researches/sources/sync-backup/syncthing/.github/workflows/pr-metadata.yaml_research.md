# sources/sync-backup/syncthing/.github/workflows/pr-metadata.yaml

Purpose: PR metadata automation, specifically label application used for release notes and policy decisions.

Important APIs/types/functions: trigger is `pull_request_target` for opened, reopened, edited, and synchronize events. Permissions are read contents and write pull requests. Job `labels` uses `srvaroa/labeler` with `GITHUB_TOKEN`.

Control flow: on eligible PR events, the workflow runs in the base repository context and applies labels according to `.github/labeler.yml`.

State and persistence behavior: labels persist on PRs. No workspace artifacts are retained.

Dependencies/integration: coupled to labeler config, GitHub PR labels, release-note generation, and policy-bot rules.

Risks/test signals: `pull_request_target` has elevated context; this workflow safely avoids checking out or running PR code, but action supply-chain trust still matters. Signal is correct labels after PR title changes or synchronization.
