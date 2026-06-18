# sources/sync-backup/syncthing/.github/workflows/build-syncthing.yaml

Purpose: primary CI, packaging, signing, release, Docker, vulnerability, lint, and metadata workflow for Syncthing. It runs on pull requests, pushes except release branches, workflow calls, and manual dispatch; release-only jobs are gated to Syncthing-owned release/nightly/tag refs.

Important APIs/types/functions: jobs include `facts`, `build-test`, aggregate `basics`, platform packaging for Windows/Linux/illumos/macOS/cross/source/Debian, Windows codesigning, macOS notarization, upgrade signing, nightly publishing, release file publishing, APT publishing, GHCR Docker image build, Docker Hub sync, `govulncheck`, `golangci`, and `meta`. It uses pinned or versioned actions, `build.go` commands, Zig cross-compilers, fpm, gh, rclone, ezapt, Sentry-independent signing utilities, and GitHub artifact upload/download.

Control flow: `facts` derives version, release kind, generation, and Go version. CI tests run across OS and Go-version matrix. Packaging jobs build artifacts and upload them. Release-gated jobs download artifacts, sign them, produce checksums/attestations, sync object storage, publish GitHub releases, publish APT, and mirror Docker images.

State and persistence behavior: persistent outputs include uploaded artifacts, GHCR/Docker Hub images, object-store release/nightly files, GitHub releases, APT repository contents, provenance attestations, signatures, and Debian packages. Build metadata is injected via env and linker flags.

Dependencies/integration: deeply integrated with `build.go`, `build.sh`, `compat.yaml`, `script` tooling, release-tools checkout, repo secrets, Dockerfiles, APT signing, code-signing/notarization services, Codecov-style coverage generation, golangci config, and meta tests.

Risks/test signals: high secret and supply-chain surface. Some actions are pinned to SHAs while core GitHub actions use major tags. Conditional release paths mean PRs do not test signing/notarization/object-store publishing. Strong signals are `basics` passing, generated artifacts for all matrices, successful signature/attestation creation, and release refs producing complete published assets.
