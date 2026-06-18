<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/.github/workflows/codeql-analysis.yml -->
# sources/user-network-fs/go-nfs/.github/workflows/codeql-analysis.yml

## Purpose
Defines the go-nfs CodeQL code-scanning workflow.

## Important APIs, Types, and Functions
The workflow triggers on push, pull request, and a weekly Wednesday schedule; job checks out code, initializes CodeQL, autobuilds, and analyzes.

## Control Flow
For PRs it fetches depth 2 and checks out `HEAD^2` before CodeQL setup. CodeQL action v1 performs initialization and analysis.

## State and Persistence Behavior
State lives in GitHub Actions runs and uploaded code-scanning results.

## Dependencies and Integration Points
Integrates with GitHub CodeQL actions and repository build tooling.

## Risks and Edge Cases
Uses old action versions (`checkout@v2`, CodeQL v1) and a brittle PR checkout command. Autobuild may not fully represent Go module tests.

## Test Signals
Signals are CodeQL alerts and workflow pass/fail status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/.github/workflows/codeql-analysis.yml -->
