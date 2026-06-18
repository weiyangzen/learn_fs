<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/create-branches -->
# sources/user-network-fs/mergerfs/buildtools/create-branches

## Purpose

This developer helper creates two 1 GiB loopback image files under `/tmp`, formats them as ext4, creates mountpoints, and mounts them for local mergerfs branch testing. The source was read as a complete 14-line file (313 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

The file is declarative or linear automation: commands run in order, with build arguments/environment controlling clone/build/install/publish steps.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `truncate`, `mkfs.ext4`, `sudo`, `mount`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/create-branches -->
