# sources/sync-backup/restic/helpers/verify-release-binaries.sh

## Purpose

This Bash script verifies a restic release by checking published checksums/signatures, comparing the source tarball to the tagged repository, rebuilding release binaries in a regenerated builder container, and verifying that published Docker images contain the same binaries as the release artifacts.

## Important APIs, Types, and Functions

- Requires arguments: `restic_version` and `go_version`.
- Uses strict mode `set -euo pipefail`.
- `set_invalid` records warnings and flips `is_valid` to `0` without immediately aborting all checks.
- `highlight` prints section headers.
- Downloads release tarball signature, `SHA256SUMS`, and its signature from GitHub.
- Imports `https://restic.net/gpg-key-alex.asc` into a temporary `GNUPGHOME` and verifies signatures.
- Downloads every file listed in `SHA256SUMS` and verifies checksums.
- Extracts the source tarball, clones the matching tag, removes `.git`, and diffs source trees.
- Clones `restic/builder`, rebuilds `restic/builder:tmp` with `GO_VERSION`, and reruns `helpers/build-release-binaries/main.go`.
- `extract_docker(image, docker_platform, restic_platform)` pulls a platform-specific Docker image, saves it, extracts `usr/bin/restic` from layers, bzip2-compresses it, and checks it against release checksums.
- Loops over `restic/restic` and `ghcr.io/restic/restic` images for arm/v7, arm64, 386, and amd64.

## Control Flow

The script creates a temporary directory under the current directory, enters it, and performs verification in sections. Some mismatches call `set_invalid` so later checks still run. Fatal command failures still stop due to `set -e`. If any soft validation failed, it prints a failure header and exits `1`. If all validations pass, it removes the temporary directory and exits successfully.

## State and Persistence Behavior

It creates a temporary workspace, a temporary GPG home, cloned repositories, downloaded release artifacts, rebuilt output, Docker image tar exports, and extracted Docker binary directories. On success it removes the workspace. On validation failure it leaves the workspace for inspection.

## Dependencies and Integration Points

It depends on Bash, curl, gpg, shasum, git, diff, Docker 25+ for platform image pulls/saves, tar, bzip2, and a working network. It integrates with GitHub Releases, the restic Git tag, `restic/builder`, Docker Hub `restic/restic`, GHCR `ghcr.io/restic/restic`, and `helpers/build-release-binaries/main.go`.

## Risks and Edge Cases

- `mkdir -p 700 $GNUPGHOME` appears intended to set permissions but actually creates directories named `700` and `$GNUPGHOME`; it does not chmod the GPG home. GPG may warn or fail depending on environment.
- Parsing `SHA256SUMS` with `cut -d " " -f 3` assumes the checksum file spacing/format.
- Docker layer extraction scans all layer blobs and expects exactly one `usr/bin/restic`; multiple matches are flagged.
- The script requires substantial disk/network resources and Docker privileges.
- A hard failure before the final cleanup leaves temporary files by design for debugging.

## Test Signals

The script is itself an end-to-end release verification signal. A successful run means release artifacts match checksums/signatures, source tarball matches the tag, binaries are reproducible with the specified Go version, and Docker images embed release-equivalent binaries.
