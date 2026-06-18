# sources/security-integrity/ecryptfs-utils/scripts/build-full-tarball.sh

Purpose: legacy release helper that packages userspace and kernel eCryptfs trees into a dated tarball.

Important APIs/commands: copies `ecryptfs-utils-git` and `ecryptfs-kernel-git`, bootstraps each with aclocal/libtoolize/automake/autoconf, symlinks kernel `src`, removes build/VCS cruft, creates `.tar.bz2`, and removes the staging tree.

Control flow/state: destructive cleanup happens in copied staging directories and final tarball is written in the caller directory.

Dependencies/integration: assumes sibling git trees, kernel version directories, Autotools, and tar.

Risks: many unquoted variables and broad `find ... -exec rm -rf` patterns. Safe only in expected legacy release layout.

Test signals: successful tarball build and clean staged contents.
