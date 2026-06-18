# sources/sync-backup/syncthing/.github/dependabot.yml

Purpose: Dependabot configuration for monthly dependency updates. It covers GitHub Actions workflows and direct Go module dependencies, using cooldown periods and grouping to reduce update noise.

Important APIs/types/functions: top-level `version: 2`; two `updates` entries configure `package-ecosystem: github-actions` and `gomod`, both at `/`, monthly schedule, `cooldown.default-days: 14`, and grouped version updates. Go modules are restricted to `dependency-type: direct`.

Control flow: Dependabot periodically scans, waits out cooldown windows, groups matching updates into PRs, and avoids indirect Go dependency churn unless required by direct updates.

State and persistence behavior: no app state; Dependabot state exists in GitHub PRs and update metadata.

Dependencies/integration: integrates with GitHub Actions dependency manifests, `go.mod`, `go.sum`, labeler/policy rules for dependency PRs, and CI gates.

Risks/test signals: grouped updates can make regressions harder to isolate. Direct-only Go updates may leave vulnerable transitive dependencies until direct parents move. Signals are successful monthly PRs labeled/reviewed by automation and passing build workflows.
