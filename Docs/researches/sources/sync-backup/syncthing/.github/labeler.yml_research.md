# sources/sync-backup/syncthing/.github/labeler.yml

Purpose: configuration for the PR metadata labeler. It maps conventional commit-style PR titles to GitHub labels used for triage and release-note categorization.

Important APIs/types/functions: `version: 1` and `labels` entries match `title` regexes: `^feat\b` to `enhancement`, `^fix\b` to `bug`, `^docs\b` to `documentation`, `^chore\b` and `^refactor\b` to `chore`, `^build\b` to `build`, and `^build\(deps\)\b` to `dependencies`.

Control flow: the PR metadata workflow runs the labeler on `pull_request_target` events and applies labels based on the title.

State and persistence behavior: no local state; labels persist on pull requests and affect release notes and policy rules.

Dependencies/integration: tied to `.github/workflows/pr-metadata.yaml`, `.github/release.yml`, and `.policy.yml` conventional-title approval rule.

Risks/test signals: regex ordering and overlaps mean dependency PRs can receive both build-related and dependency semantics depending on labeler behavior. Signal is PR labels matching title conventions and release notes grouping correctly.
