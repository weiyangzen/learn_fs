# sources/sync-backup/git-lfs/.github/workflows/release.yml

Purpose: tag-triggered git-lfs release workflow that builds, signs/notarizes, packages, and uploads release artifacts for Windows, macOS, Linux packages, and ARM Linux packages.

Important APIs/types/functions: trigger `push.tags: '*'`, `GOTOOLCHAIN=local`, jobs `build-windows`, `build-macos`, `build-main`, `build-docker`, and `build-docker-arm`; Actions `checkout@v6`, `setup-go@v6`, `download-artifact@v8`, `upload-artifact@v7`, `azure/artifact-signing-action@v2.0.0`, Git for Windows SDK, and Makefile targets for release, Windows staging/signing/rebuild, Darwin release, certificate import, and packagecloud upload.

Control flow: Windows builds zip assets for amd64/386/arm64, stages Windows installer/signing phases, signs stage1 and stage2 executables with Azure code signing, rebuilds release artifacts, and uploads `windows-assets`. macOS builds release assets, writes/imports Developer ID certificate from secrets, runs Darwin release/notarization tooling, and uploads `macos-assets`. Main Linux job downloads Windows/macOS artifacts, builds Linux release assets with `CGO_ENABLED=0`, replaces generated Windows/Darwin assets with signed/notarized ones, and uploads a consolidated `release-assets` bundle. Docker jobs build Linux packages and upload to packagecloud except for pre-release tags; ARM uses `ubuntu-24.04-arm` and arm64 docker targets.

State/persistence behavior: release artifacts are staged under `bin/releases`, temporary signing folders, `release-assets/bin`, and workflow artifacts. Secrets provide signing credentials, macOS certificates, notarization credentials, and packagecloud token. Package upload persists externally to packagecloud for non-pre-releases.

Dependencies/integration: integrates GitHub Actions environments, Go, Ruby/asciidoctor/packagecloud gems, Chocolatey, InnoSetup, jq, zip, Git for Windows SDK, Azure code signing, Apple signing/notarization, docker packaging repositories, and project Makefile/script release targets.

Risks/test signals: high-risk areas are secret availability, signing endpoint configuration, certificate import, artifact name/path conventions, cross-job artifact replacement, pre-release tag shell condition, and ARM runner availability. Tests/signals include signed executable validation, notarization success, expected artifact set in `release-assets`, packagecloud dry-run or controlled release, and reproducible `git describe` from full-depth checkout.
