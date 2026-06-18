# File Research: sources/local-fs/ocfs2-tools/extras/Makefile

## Role

This makefile builds uninstalled developer/diagnostic helper programs for OCFS2.

## Programs

It defines uninstalled targets for hardlink discovery, duplicate extent discovery, inode path lookup, random bit setting, lock resource decode/encode, journal dirty marking, allocation fragmentation discovery, group computation, metadata ECC checking, and slotmap resizing.

## Build Pattern

Each helper has a single C file, object list, and link rule. All helpers link against the static `../libocfs2/libocfs2.a`, `com_err`, and AIO.

## Distribution

All helper source files are included in `DIST_FILES`, but the programs are not installed through normal install rules.
