# sources/sync-backup/kopia/.github/auto-merge.yml

Purpose: dependency auto-merge allowlist for Dependabot PRs.

Important APIs/types/functions: match rules by `dependency_name` and `update_type`, covering selected Go, Playwright, telemetry, Prometheus, React, and test/development dependencies. Comments explicitly exclude large Electron dependencies.

Control flow: consumed by the auto-merge GitHub Action; matching Dependabot updates are eligible for approval/merge.

State and persistence: static policy file.

Dependencies and integration points: referenced by `.github/workflows/auto-merge.yml`; relies on dependency-review/test CI for safety.

Risks: regex-like dependency names depend on action matching semantics. Overbroad minor auto-merge rules can admit regressions if tests are insufficient.

Test signals: auto-merge workflow plus CI outcomes are the practical validation.
