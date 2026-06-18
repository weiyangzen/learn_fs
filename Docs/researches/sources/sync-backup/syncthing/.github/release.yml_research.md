# sources/sync-backup/syncthing/.github/release.yml

Purpose: GitHub release-note generation configuration. It excludes dependency-labeled PRs and groups remaining changes into Fixes, Features, and Other categories.

Important APIs/types/functions: `changelog.exclude.labels` contains `dependencies`; `categories` maps `bug` to `Fixes`, `enhancement` to `Features`, and wildcard labels to `Other`.

Control flow: GitHub release tooling reads this when generating release notes, using PR labels supplied by manual triage and the labeler workflow.

State and persistence behavior: no local state; output becomes release-note text on GitHub releases.

Dependencies/integration: depends on consistent labels from `.github/labeler.yml`, PR metadata automation, and maintainer triage.

Risks/test signals: dependency work is intentionally omitted from generated notes, which can hide important security dependency bumps unless called out manually. Signal is generated releases sorted into the intended categories.
