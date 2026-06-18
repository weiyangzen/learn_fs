# File Research: sources/virtualization/libblockdev/src/lib/blockdev.pc.in

## Role
Pkg-config template for consumers of the core BlockDev library.

## Contents
- Defines substituted `prefix`, `exec_prefix`, `includedir`, and `libdir`.
- Publishes package metadata:
  - `Name: BlockDev`;
  - description for low-level block-device operations;
  - upstream URL;
  - `Version: @VERSION@`.
- Declares `Requires: glib-2.0`.
- Exposes link flags `-L${libdir} -lblockdev`.
- Exposes include flag `-I${includedir}`.

## Dependencies and Interactions
- Installed by `src/lib/Makefile.am`.
- Complements installed headers under `$(includedir)/blockdev`.

## Filesystem/Storage Relevance
This file lets external C projects discover compile and link flags for using libblockdev's storage/plugin initialization API.
