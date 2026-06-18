<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/build-release -->
# sources/user-network-fs/mergerfs/buildtools/build-release

## Purpose

This Python release orchestrator runs podman builds for one or more generated containerfiles. It can install qemu/binfmt support, prune podman state between builds, bind a local or remote git repo into builds, export packages into a package directory, and append per-containerfile results to `build-report.txt`. The source was read as a complete 178-line file (6099 bytes).

## Important APIs, Types, and Functions

Python functions: `build`, `setup`, `setup_binfmt`, `podman_cleanup`, `parse_args`, `should_skip`, `main`

## Control Flow

Control starts in `main()`, parses CLI arguments, optionally runs setup/cleanup, discovers matching containerfiles, then calls build orchestration helpers (`build`, `setup`, `setup_binfmt`, `podman_cleanup`, `parse_args`, `should_skip`, `main`) in sequence.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `python3`, `podman`, `git`, `apt-get`, `sudo`, `pacman`, `systemctl`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/build-release -->
