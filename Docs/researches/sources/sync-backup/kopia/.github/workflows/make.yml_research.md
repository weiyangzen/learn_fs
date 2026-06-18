# sources/sync-backup/kopia/.github/workflows/make.yml

## Purpose
Defines the main multi-platform build and publish workflow. It builds CLI and UI artifacts for Windows, Linux, macOS, and Ubuntu ARM, then stages and publishes releases from a separate Ubuntu job when the event is not a pull request and the repository is `kopia/kopia`.

## APIs, Control Flow, and Integration Points
The build matrix checks out full history, installs Go, installs platform packages, runs `make -j4 ci-setup`, installs macOS certificates when eligible, installs Windows signing tools on Windows, and runs `make ci-build` with signing/notarization secrets. It uploads packaged artifacts and raw binaries separately. The publish job downloads those artifacts, installs QEMU and Docker Buildx, imports GPG and GCS credentials through Makefile targets, runs `make stage-release`, pushes GitHub releases, publishes APT/RPM/Homebrew/Scoop/Docker, and bumps Homebrew for final non-rc tags.

## State, Persistence, and Dependencies
Build outputs persist through GitHub artifacts under `dist` and `dist_binaries`. Secret-derived state includes Apple API key files, macOS certificates, Windows signing tools, GPG keyrings, GCS credentials, and Docker login. The workflow depends heavily on Makefile release targets, `electron-builder`, GoReleaser, GitHub CLI, Docker, and cloud tooling.

## Risks and Test Signals
This file is the highest-blast-radius CI surface in the subset because it handles code signing, notarization, release publication, package repositories, Docker pushes, and formula updates. Secrets are passed only to the specific steps that need them, which limits accidental exposure. Artifact upload patterns are broad and should be reviewed when new dist files are added. The build signal includes compilation, UI packaging, UI tests, changelog generation, and release staging.
