# sources/storage-engines/raft-engine/.github/dependabot.yml

## Purpose
Configures GitHub Dependabot for the raft-engine subtree so Cargo dependency updates are proposed automatically.

## Important APIs, Types, And Functions
The YAML uses Dependabot schema `version: 2` with one `updates` entry. It targets `package-ecosystem: cargo`, `directory: /`, and a daily schedule.

## Control Flow
There is no runtime control flow. GitHub's Dependabot service reads this file and periodically evaluates Cargo manifests and lockfiles at the repository root.

## State And Persistence Behavior
The file does not affect engine persistence. Its state impact is repository metadata: generated dependency update pull requests may later change Cargo dependency versions.

## Dependencies And Integration Points
Integrates with GitHub automation, Cargo manifest dependency declarations, and the CI workflow in `.github/workflows/rust.yml` that validates generated dependency PRs.

## Risks And Edge Cases
Daily update cadence can create frequent PR churn. It only targets the root directory, so workspace members are covered through the root workspace, but separate nested ecosystems would require more entries. Dependabot PRs are ignored by the workflow push trigger through branch filtering.

## Test Signals
Signals are operational rather than unit-test based: Dependabot PR creation, CI execution on dependency changes, and absence of stale security/dependency alerts.
