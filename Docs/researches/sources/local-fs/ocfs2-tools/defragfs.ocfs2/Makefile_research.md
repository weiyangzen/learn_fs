# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/Makefile

## Role

This makefile builds the `defragfs.ocfs2` online defragmentation tool.

## Build Inputs

It compiles `main.c`, `record.c`, and `libdefrag.c`, with headers under `include/`. It defines `VERSION`, installs under `$(root_sbindir)`, and builds the `defragfs.ocfs2.8` man page.

## Linkage

The target uses the project `$(LINK)` rule without adding extra local libraries in this makefile; required libc/kernel interfaces are used directly by the object files.

## Distribution

The distribution list includes source files, headers, and the man-page template, and creates an `include` directory in the distribution archive.
