# File Research: sources/local-fs/ocfs2-tools/debian/rules

## Role

`debian/rules` is the Debian package build script for `ocfs2-tools`.

## Build Flow

It includes quilt integration, runs `./configure` with debug disabled, dynamic control/fsck enabled, `/usr` prefix paths, and `/usr/share/man` man path, then builds with `make`.

## Install And Packaging

The install target stages into `debian/tmp`, copies vendor init/default files into Debian package names, runs `dh_install`, installs init scripts for `o2cb` and `ocfs2`, installs docs/examples/changelog, then performs Debian helper steps for stripping, compression, debconf, permissions, shared libraries, Python support, control file generation, checksums, and package build.

## Cleanup

The clean target unpatches quilt patches, removes Debian helper state, generated init/default files, vendor spec output, console shared objects, runs `make distclean`, and updates debconf translations.

## Risk Areas

This is an older debhelper-style rules file using `dh_clean -k`, `dh_pysupport`, and quilt makefile inclusion. Modern Debian tooling may require updates.
