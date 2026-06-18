<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/.github/dependabot.yml -->
# sources/user-network-fs/go-nfs/.github/dependabot.yml

## Purpose
Configures Dependabot for the go-nfs repository.

## Important APIs, Types, and Functions
The YAML declares version 2 updates for the `gomod` ecosystem at `/` on a daily schedule.

## Control Flow
GitHub Dependabot reads this file and opens dependency update PRs for Go module manifests.

## State and Persistence Behavior
State is GitHub-side scheduling and generated PRs; no runtime project state.

## Dependencies and Integration Points
Integrates with GitHub dependency management and the root `go.mod`.

## Risks and Edge Cases
Daily cadence can create noisy PRs; only Go modules are covered, not GitHub Actions versions.

## Test Signals
Signals are Dependabot PRs and GitHub dependency graph alerts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/.github/dependabot.yml -->
