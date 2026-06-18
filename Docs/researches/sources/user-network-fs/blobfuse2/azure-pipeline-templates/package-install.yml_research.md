# sources/user-network-fs/blobfuse2/azure-pipeline-templates/package-install.yml

## Purpose
This template installs distro-specific build and runtime dependencies required for Blobfuse2 Azure pipeline jobs.

## Important APIs, Types, and Functions
It uses apt, yum/dnf, zypper, and tdnf branches conditioned on `variables['distro']`. It installs compilers, git, make/cmake, Python, FUSE/FUSE3 development packages, GNU parallel, and Azure CLI for Ubuntu.

## Control Flow
For Ubuntu it handles apt locks, installs build tools, conditionally installs FUSE2 or FUSE3 based on `$(tags)`, verifies fusermount versions, and installs Azure CLI. RHEL, CentOS, Oracle, Rocky, SUSE, and Mariner branches install equivalent packages with distro-specific repository fixes.

## State and Persistence Behavior
It mutates the agent OS package state and can update system packages. No repository files are persisted.

## Dependencies and Integration Points
It is the first step of `build.yml` and underpins all Azure DevOps jobs across distro matrices.

## Risks and Edge Cases
The Ubuntu branch aggressively kills apt processes and lock holders. Distro package names and repository availability can drift. Azure CLI is installed only in Ubuntu branch, while later templates may assume `az` exists.

## Test Signals
Signals include successful package manager commands, available compiler/FUSE tools, `az --version` on Ubuntu, and later build/mount steps succeeding.
