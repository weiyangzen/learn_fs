# sources/user-network-fs/blobfuse2/.github/dependabot.yml

## Purpose
This file configures Dependabot to keep GitHub Actions and Go module dependencies current.

## Important APIs, Types, and Functions
The two `updates` entries use Dependabot package ecosystems `github-actions` and `gomod`, both rooted at `/` and scheduled daily.

## Control Flow
Dependabot scans the repository root each day for workflow action references and `go.mod` dependency changes, then opens pull requests when updates are available.

## State and Persistence Behavior
There is no runtime state in the repo. Dependabot state and PR metadata live in GitHub. Generated PRs can mutate workflow versions and Go dependency files once merged.

## Dependencies and Integration Points
This integrates with GitHub Dependabot and indirectly affects every workflow that references external actions plus the Go module graph used by CI.

## Risks and Edge Cases
Daily updates can create high PR volume, and major action upgrades may break pinned workflow assumptions. No grouping, ignore rules, or labels are configured, so triage policy is entirely external.

## Test Signals
Signals are Dependabot PR creation, GitHub Actions CI on dependency update PRs, and successful `go mod` resolution after Dependabot updates.
