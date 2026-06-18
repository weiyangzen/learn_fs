# sources/sync-backup/kopia/Makefile

## Purpose
Central build, test, lint, release, provider-test, UI, and publication orchestrator for Kopia. GitHub Actions mostly delegate to targets in this Makefile, making it the main integration point for CI and developer workflows.

## APIs, Control Flow, and Integration Points
The Makefile includes `tools/tools.mk`, computes Go source lists, defines build flags that inject version/commit/repository metadata, and chooses `kopia_ui_embedded_exe` paths by `GOOS`/`GOARCH`. Core targets include `install`, `lint`, `lint-*`, `check-locks`, `ci-setup`, `kopia-ui`, `kopia-ui-test`, platform-specific binary builds, `ci-build`, `goreleaser`, `ci-tests`, `provider-tests`, `license-check`, endurance/recovery/robustness/stress/VSS tests, HTML UI E2E tests, release staging, GitHub release pushes, package repository publishing, Docker publishing, and performance benchmark automation.

## State and Persistence
It creates and consumes `dist/`, `dist_binaries/`, `.logs/`, `.tmp.*.json`, `.release/`, coverage files, downloaded tools under `tools/.tools`, node modules under `app/`, GPG/GCS credentials, Apple API key files, signed binaries, checksums, package repositories, and cloud benchmark instances. Several targets export environment variables to test binaries, including `KOPIA_EXE`, `KOPIA_LOGS_DIR`, `KOPIA_PROVIDER_TEST`, and stress/debug flags.

## Risks and Test Signals
The file has high operational blast radius because release targets can sign and publish artifacts to GitHub, package repositories, Docker Hub, Homebrew, and Scoop. Conditional platform branches are dense, and typos in paths or architecture mappings can break packaging. It provides the repository's strongest test signals through unit, race, provider, stress, robustness, socket activation, VSS, compatibility, coverage, and HTML UI E2E targets.
