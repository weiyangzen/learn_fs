# sources/sync-backup/kopia/.github/workflows/ossf-scorecard.yml

## Purpose
Runs OpenSSF Scorecard analysis for supply-chain posture. It is triggered by branch protection changes, pushes to `master`, and a weekly schedule so the "Maintained" check stays current.

## APIs, Control Flow, and Integration Points
The workflow uses `permissions: read-all` by default and grants `security-events: write` plus `id-token: write` to the analysis job. It checks out the repository without persisted credentials, runs pinned `ossf/scorecard-action`, emits SARIF to `results.sarif`, uploads that SARIF to GitHub code scanning with category `ossf`, and also stores the SARIF as a short-retention artifact.

## State, Persistence, and Dependencies
Persistent state appears in GitHub code scanning, the Scorecard published result, and a five-day artifact. The workflow depends on Scorecard's external checks and GitHub's SARIF ingestion.

## Risks and Test Signals
The permissions are intentionally narrow except for OIDC publication and SARIF upload. Because Scorecard behavior evolves outside this repo, pinned action versions help stability but may lag new checks. The signal is not functional testing; it is a governance and supply-chain health indicator for branch protection, token permissions, maintained status, dependency update behavior, and related repository practices.
