<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/setupUBN.sh -->
# sources/user-network-fs/blobfuse2/setup/setupUBN.sh

## Purpose
Ubuntu setup script for installing development/runtime dependencies, Microsoft package repositories, Blobfuse2, and Azure security pack setup.

## Important APIs, Types, and Functions
Runs `../go_installer.sh ../../`, installs packages with `apt`, enables `user_allow_other` in `/etc/fuse.conf`, adds Microsoft package signing/repo config, installs `blobfuse2`, prints version, and calls `vmSetupAzSecPack.sh`.

## Control Flow and State
The script executes sequentially with many `sudo` mutations: package database updates, package installs, `/etc/fuse.conf` edit, repository addition, and Azure security extension setup. It does not set `set -e`, so failures may not abort later steps.

## Dependencies and Integration Points
Requires Ubuntu, sudo, apt, wget, add-apt-repository, Microsoft package endpoints, and sibling scripts. Integrates with developer/VM provisioning.

## Risks and Edge Cases
Uses deprecated `apt-key`. Unconditional `sed` can duplicate or alter fuse config unexpectedly. Lack of strict error handling can hide failed installs. Calling `vmSetupAzSecPack.sh` triggers Azure login and VM extension operations, which may be surprising for a dependency setup script.

## Test Signals
`go version`, successful package installation, `blobfuse2 --version`, and AzSecPack status output indicate setup progress.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/setupUBN.sh -->
