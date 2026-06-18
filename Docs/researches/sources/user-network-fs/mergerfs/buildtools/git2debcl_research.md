<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/git2debcl -->
# sources/user-network-fs/mergerfs/buildtools/git2debcl

## Purpose

This shell script converts git tag history into Debian changelog entries. It guesses package version/distribution/codename when requested, walks reverse-version-sorted tags, extracts non-merge commits, and formats Debian changelog stanzas. The source was read as a complete 202-line file (5043 bytes).

## Important APIs, Types, and Functions

shell functions: `usage`, `git_tags`, `git_log`, `git_author_and_time`, `git_version`, `guess_distro`, `guess_codename`

## Control Flow

The script runs top-level shell logic and helper functions (`usage`, `git_tags`, `git_log`, `git_author_and_time`, `git_version`, `guess_distro`, `guess_codename`). It exits early on invalid inputs or unsupported distributions and otherwise delegates work to git, package managers, podman, make, or mike.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `git`

## Risks and Edge Cases

Risks are environment-dependent failures, privileged package-manager/podman operations, distro detection drift, accidental publication or cleanup, and reproducibility issues when git refs, package repositories, or container images change.

## Test Signals

Shellcheck/argument validation where applicable, container build dry runs for representative distro/arch targets, package artifact checks, and docs build/publish tests against a disposable remote or local mike output.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/buildtools/git2debcl -->
