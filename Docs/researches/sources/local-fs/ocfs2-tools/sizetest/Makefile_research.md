# File Research: sources/local-fs/ocfs2-tools/sizetest/Makefile

## Purpose
Builds the uninstalled `sizetest.ocfs2` utility.

## Main Behavior
- Includes common project build rules from `../Preamble.make` and `../Postamble.make`.
- Defines `UNINST_PROGRAMS = sizetest.ocfs2`.
- Adds `-I$(TOPDIR)/include` and `-DVERSION="$(VERSION)"`.
- Compiles `sizetest.c` into `sizetest.o`.
- Links `sizetest.ocfs2` with `$(LIBOCFS2_DEPS)` through the shared `$(LINK)` rule.
- Marks `sizetest.c` as the distribution file.

## Dependencies
- Top-level OCFS2 tools make infrastructure.
- `libocfs2.a`.
