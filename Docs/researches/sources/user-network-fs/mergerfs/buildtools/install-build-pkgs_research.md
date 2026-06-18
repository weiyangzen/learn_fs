<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/install-build-pkgs -->
# sources/user-network-fs/mergerfs/buildtools/install-build-pkgs

## Purpose

This container provisioning script installs distro-specific compiler and packaging dependencies, selects the newest available C++ compiler/toolset where possible, writes `/tmp/build-env`, and verifies C++20 support before package builds proceed. The source was read as a complete 162-line file (3940 bytes).

## Important APIs, Types, and Functions

functions: `main` shell functions: `write_gcc_env`, `write_toolset_env`, `latest_apt_gxx`, `latest_dnf_toolset`, `latest_yum_toolset`, `version_gt`, `check_cxx20`

## Control Flow

The script runs top-level shell logic and helper functions (`write_gcc_env`, `write_toolset_env`, `latest_apt_gxx`, `latest_dnf_toolset`, `latest_yum_toolset`, `version_gt`, `check_cxx20`). It exits early on invalid inputs or unsupported distributions and otherwise delegates work to git, package managers, podman, make, or mike.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `dnf`, `yum`, `apt-get`, `git`, `fakeroot`, `make`, `zypper`, `apk`, `pkg`, `pacman`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/install-build-pkgs -->
