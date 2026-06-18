# sources/sync-backup/kopia/.github/workflows/license-check.yml

## Purpose
Runs dependency license validation for pull requests and pushes to `master`. It verifies both Go and Electron UI dependency license policy through the top-level `make license-check` target.

## APIs, Control Flow, and Integration Points
The workflow checks out full history, installs Go based on `go.mod`, runs `go mod vendor`, and then calls `make license-check`. The Makefile target combines `wwhrd check` for Go modules with `npx license-checker --summary --production --onlyAllow "$(ALLOWED_LICENSES)"` for app production dependencies.

## State, Persistence, and Dependencies
The workflow mutates the workspace by creating a `vendor/` tree before license checking. It does not upload artifacts. The policy is split between `.wwhrd.yml` for Go dependency allow/deny behavior and `ALLOWED_LICENSES` in the Makefile for npm production dependency checks.

## Risks and Test Signals
Because `go mod vendor` runs before `wwhrd`, license results may depend on module graph resolution at the current commit. The npm lane uses production dependencies only, so dev tooling licenses are not covered by this CI gate. The signal is a compliance gate rather than functional test coverage; failures indicate a dependency policy issue or a dependency metadata mismatch.
