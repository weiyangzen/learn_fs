# sources/storage-engines/pebble/.github/workflows/code-cover-gen.yaml

## Purpose
`code-cover-gen.yaml` generates before/after PR coverage artifacts for changed Go packages without requiring repository secrets on untrusted pull-request code.

## Important APIs, types, and functions
It triggers on pull-request open/reopen/synchronize against `master`, checks out the PR head SHA with full history, sets up Go 1.26, uses `gh pr view`, `git rev-parse`, `scripts/changed-go-pkgs.sh`, `scripts/pr-codecov-run-tests.sh`, and uploads `cover-*.json` artifacts.

## Control flow
The workflow computes the PR commit count, derives the base SHA as `HEAD~NUM_COMMITS`, computes changed packages, stores base and package list in `GITHUB_ENV`, copies the coverage script to runner temp, generates "after" coverage at the PR head, checks out the base SHA, generates "before" coverage with the same script copy, and uploads both JSON files as an artifact named `cover`.

## State and persistence behavior
It writes transient artifact files under `artifacts/` and uploads them to GitHub Actions storage. It intentionally does not use secrets.

## Dependencies and integration points
The publish workflow consumes the uploaded artifact. The logic depends on GitHub CLI authentication via `GH_TOKEN`, full git history, and repository coverage scripts.

## Risks and edge cases
Deriving base SHA from commit count can be wrong for complex PR histories. The changed package list is passed through environment variables and shell quoting; packages with unusual whitespace would be risky. Checking out the base after running untrusted PR code is acceptable because the artifact-generation job has no secrets.

## Test signals
Expected signals are two JSON coverage files named with PR/head/base identifiers, correct changed package selection, and successful artifact upload for representative PR shapes.
