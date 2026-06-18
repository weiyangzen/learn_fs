# sources/sync-backup/bup/dev/prep-for-debianish-build

## Purpose
Installs Debian/Ubuntu-style build and test dependencies for bup CI or local setup.

## Important APIs, Types, and Functions
Accepts optional `pyxattr` or `xattr` selector and installs packages including ACL/xattr tools, compilers, git, graphviz, pandoc, libacl/readline dev packages, pytest/xdist, tornado, FUSE, rsync, rdiff-backup, and duplicity.

## Control Flow
Validates xattr flavor, exports `DEBIAN_FRONTEND=noninteractive`, runs `apt-get update`, and installs the package list.

## State and Persistence Behavior
Mutates system package state.

## Dependencies and Integration Points
Used by Cirrus Debian tasks before configure and make targets.

## Risks and Test Signals
Risks include package name drift and root/package-manager requirements. Signal is successful apt install.
