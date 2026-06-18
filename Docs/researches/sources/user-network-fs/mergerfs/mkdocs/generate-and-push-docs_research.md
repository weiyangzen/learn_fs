<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/mkdocs/generate-and-push-docs -->
# sources/user-network-fs/mergerfs/mkdocs/generate-and-push-docs

## Purpose

This docs publishing script uses mike to clear remote docs versions, deploy `master` as `latest`, iterate non-release-candidate tags containing `mkdocs.yml`, deploy each version, set the default version, and restore the original branch. The source was read as a complete 32-line file (789 bytes).

## Important APIs, Types, and Functions

No code APIs are declared; the important surface is the file content/metadata consumed by external tooling.

## Control Flow

The file is declarative or linear automation: commands run in order, with build arguments/environment controlling clone/build/install/publish steps.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `git`, `mike`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/mkdocs/generate-and-push-docs -->
