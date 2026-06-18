<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/containerimage/Containerfile -->
# sources/user-network-fs/mergerfs/buildtools/containerimage/Containerfile

## Purpose

This two-stage container definition builds a static mergerfs install from a git repository/branch on Alpine, archives the install tree, then produces a minimal runtime image with `mergerfs` as entrypoint. The source was read as a complete 19-line file (587 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

The file is declarative or linear automation: commands run in order, with build arguments/environment controlling clone/build/install/publish steps.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `apk`, `git`, `make`, `mount`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/containerimage/Containerfile -->
