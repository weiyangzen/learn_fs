# File Research: sources/virtualization/libblockdev/src/Makefile.am

## Role
Top-level Automake entry for `src/`. It defines the build traversal order for libblockdev's source subtree.

## Contents
- `SUBDIRS = utils plugins lib python` builds utilities first, then plugin shared libraries, then the central `libblockdev` library, then Python bindings.
- `MAINTAINERCLEANFILES = Makefile.in` marks the generated Automake output as maintainer-clean.

## Dependencies and Interactions
- The ordering is meaningful: `src/lib/Makefile.am` links against `../utils/libbd_utils.la`, while plugins also link against utils.
- `plugins` is built before `lib`, but the core library dynamically loads plugin shared objects at runtime rather than statically linking them.

## Filesystem/Storage Relevance
This file is infrastructure only. Its main filesystem relevance is that it arranges build order for block-device utility code, filesystem/block plugins, the loader library, and bindings.
