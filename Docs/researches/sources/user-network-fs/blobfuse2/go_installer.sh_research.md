## sources/user-network-fs/blobfuse2/go_installer.sh

Purpose: Installs a pinned Microsoft build of Go, intended for FIPS-capable builds using `systemcrypto`.

Important flow: Uses `set -euo pipefail`, trims the work directory argument, chooses `GO_VERSION` default `1.26.3`, detects architecture, downloads the tarball and SHA256 sidecar from `aka.ms`, verifies checksum, stages extraction in `/usr/local/go.new`, validates `go version`, requires `MICROSOFT_REVISION`, atomically swaps `/usr/local/go`, symlinks `go` and `gofmt` into `/usr/bin`, and removes the tarball.

State and dependencies: Mutates `/usr/local/go`, `/usr/bin/go`, `/usr/bin/gofmt`, and downloads into the provided work dir. Requires sudo, wget, tar, sha256sum, awk, and network.

Risks: It assumes Microsoft aka.ms sidecar availability and the version naming convention. Existing Go is moved aside then deleted after successful swap. Architecture detection uses `hostnamectl`, which may not exist in minimal containers. Strong checksum and staging behavior reduce partial-install risk.
