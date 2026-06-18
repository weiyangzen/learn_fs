<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/debian/rules -->
# sources/user-network-fs/mergerfs/debian/rules

## Purpose

This Debian packaging makefile delegates debhelper targets, overrides auto-build to run `make release`, and overrides auto-install to install mergerfs into the Debian package staging directory with `/usr` as prefix. The source was read as a complete 16-line file (213 bytes).

## Important APIs, Types, and Functions

make targets: `%`, `override_dh_auto_build`, `override_dh_auto_install`

## Control Flow

The file is declarative or linear automation: commands run in order, with build arguments/environment controlling clone/build/install/publish steps.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `make`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/debian/rules -->
