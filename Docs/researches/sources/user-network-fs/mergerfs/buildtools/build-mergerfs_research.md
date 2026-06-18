<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/build-mergerfs -->
# sources/user-network-fs/mergerfs/buildtools/build-mergerfs

## Purpose

This container-side shell script clones a requested mergerfs branch/repository into `/tmp/build`, selects a package build path based on the distribution package manager, and copies produced `.deb`, `.rpm`, or tarball artifacts into `/build`. The source was read as a complete 76-line file (1470 bytes).

## Important APIs, Types, and Functions

shell functions: `rpmbuild_flags`

## Control Flow

The script runs top-level shell logic and helper functions (`rpmbuild_flags`). It exits early on invalid inputs or unsupported distributions and otherwise delegates work to git, package managers, podman, make, or mike.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `git`, `apt-get`, `make`, `dnf`, `yum`, `apk`, `pkg`, `pacman`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/build-mergerfs -->
