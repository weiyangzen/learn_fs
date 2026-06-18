<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/detect-local-target -->
# sources/user-network-fs/mergerfs/buildtools/detect-local-target

## Purpose

This bash helper maps the local architecture and `/etc/os-release` distribution/version into a `buildtools/containerfiles` target name such as `debian:13.amd64`, including derivative and short-version fallbacks. The source was read as a complete 119-line file (3112 bytes).

## Important APIs, Types, and Functions

shell functions: `detect_arch`, `detect_distro`, `find_containerfile`, `main`

## Control Flow

The script runs top-level shell logic and helper functions (`detect_arch`, `detect_distro`, `find_containerfile`, `main`). It exits early on invalid inputs or unsupported distributions and otherwise delegates work to git, package managers, podman, make, or mike.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

dependencies are indirect through including translation units or repository tooling.

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/detect-local-target -->
