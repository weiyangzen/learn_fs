# sources/sync-backup/kopia/.github/workflows/dependency-review.yml

Purpose: GitHub dependency review workflow for pull requests.

Important APIs/types/functions: `pull_request` trigger, read-only contents permission, checkout action pinned by SHA, and `actions/dependency-review-action` pinned by SHA.

Control flow: checks dependency manifest changes for vulnerable packages and reports/fails according to action configuration.

State and persistence: no repo state; produces PR check annotations/status.

Dependencies and integration points: complements Dependabot and auto-merge policy.

Risks: only scans changed manifests in PR context; action pin must be updated for fixes.

Test signals: dependency review check result on PRs.
