# sources/sync-backup/kopia/.chglog/config.yml

Purpose: main Kopia changelog generator configuration.

Important APIs/types/functions: GitHub style, `CHANGELOG.tpl.md`, repository URL `kopia/kopia`, scope filters, custom grouping/title order, conventional header pattern, and `BREAKING CHANGE` notes.

Control flow: static changelog tooling input; parses commit type/scope/subject and groups by scope.

State and persistence: static config only.

Dependencies and integration points: intended to match `.github/workflows/check-pr-title.yml` scopes.

Risks: missing scopes silently omit commits from generated changelog.

Test signals: no direct tests.
