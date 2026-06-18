# sources/user-network-fs/blobfuse2/.github/workflows/codespell.yml

## Purpose
This workflow checks repository text and filenames for common spelling mistakes.

## Important APIs, Types, and Functions
It uses `actions/checkout@v6` and `codespell-project/actions-codespell@master`. Options enable filename checks, skip binary/vendor/noisy paths, and define an ignore word list for project-specific tokens.

## Control Flow
The job runs on pushes to `main` and pull requests to `main` or `blobfuse/2.*`, checks out the repository, then invokes codespell with the configured skip and ignore settings.

## State and Persistence Behavior
There is no persistent state. Failures are reported as workflow errors.

## Dependencies and Integration Points
It integrates with GitHub PR checks and protects code, comments, docs, workflow names, and filenames from spelling regressions.

## Risks and Edge Cases
The action is referenced from `master`, not a version tag or commit. The skip list and ignore list are broad enough to hide some real mistakes. Codespell can produce false positives on domain-specific storage terms.

## Test Signals
Signals are a clean codespell job on PRs and intentional typo test PRs failing unless covered by explicit ignore rules.
