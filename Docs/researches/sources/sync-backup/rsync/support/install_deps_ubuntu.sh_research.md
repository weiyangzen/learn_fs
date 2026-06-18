<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/install_deps_ubuntu.sh -->
# sources/sync-backup/rsync/support/install_deps_ubuntu.sh

Purpose: convenience script for installing rsync build dependencies on Ubuntu/Debian systems.

Important APIs/types/functions: no functions; it runs a sequence of `sudo apt install -y` commands for compiler, documentation, ACL/xattr, checksum, compression, and OpenSSL development packages.

Control flow: invoke apt for base tools (`gcc`, `g++`, `gawk`, `autoconf`, `automake`, `python3-cmarkgfm`), then separate package groups for ACL, attr, xxhash, zstd, lz4, and OpenSSL.

State and persistence behavior: mutates the host package database and installs system packages via sudo.

Dependencies and integration points: depends on bash, sudo, apt, and Debian-family package names. It prepares the environment for configuring/building rsync and related docs/features.

Risks: no `set -e`, so a failed install command may not stop later commands. It assumes package names and repository availability. It is intentionally distro-specific and should not be run blindly in non-Debian environments.

Test signals: on a fresh Ubuntu/Debian container, execution should install all listed packages and leave the rsync configure/build able to find ACL, xattr, xxhash, zstd, lz4, and OpenSSL headers.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/install_deps_ubuntu.sh -->
