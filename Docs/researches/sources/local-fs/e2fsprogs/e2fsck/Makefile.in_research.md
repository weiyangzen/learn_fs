# File Research: sources/local-fs/e2fsprogs/e2fsck/Makefile.in

## Purpose
Autoconf makefile template for building, testing, installing, and cleaning the `e2fsck` checker and related helper programs/manpages.

## Build Contents
- Builds primary `e2fsck` from pass modules, journal/recovery/revoke, directory metadata helpers, problem/message handling, quota, extent rebuild, readahead, logging, and encrypted file support.
- Supports normal, static, and profiled binaries.
- Builds test/helper targets including `tst_refcount`, `tst_region`, `tst_problem`, `tst_logfile`, `extend`, `flushb`, `iscan`, and `iscan.static`.
- Generates `e2fsck.8` and `e2fsck.conf.5` from `.in` templates through substitution.

## Install Behavior
- Installs `e2fsck` into `$(root_sbindir)`.
- Links `fsck.ext2`, `fsck.ext3`, and `fsck.ext4` to `e2fsck`.
- Installs manpages and links filesystem-specific fsck manpages to `e2fsck.8`.

## Integration
This makefile is the authoritative local build map for which e2fsck modules are linked into the main checker. Files such as `emptydir.c`, `extend.c`, `flushb.c`, and `iscan.c` are not part of the main `OBJS` list except where explicitly built as helper targets.

## Risks / Notes
- Dependency lines are generated and occupy much of the file; updates to included headers or sources require dependency regeneration.
- Optional `MTRACE` and profiling blocks are present but commented/configuration-driven.
