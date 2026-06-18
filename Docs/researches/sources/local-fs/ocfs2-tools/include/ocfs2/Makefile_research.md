# File Research: sources/local-fs/ocfs2-tools/include/ocfs2/Makefile

## Purpose

Build/install rules for public `ocfs2` headers.

## Main Contents

- Includes top-level make preamble/postamble.
- Generates `ocfs2_err.h` by copying it from `libocfs2`.
- Lists public headers: `ocfs2.h`, `jbd2.h`, `bitops.h`, `byteorder.h`, `kernel-rbtree.h`, and `image.h`.
- Defines `HEADERS_SUBDIR = ocfs2` for installation pathing.
- Adds a clean rule to remove generated `ocfs2_err.h`.

## Dependencies and Integration

- Depends on `$(TOPDIR)/libocfs2/ocfs2_err.h`, building it via `make -C $(TOPDIR)/libocfs2 ocfs2_err.h` when needed.

## Research Notes

- Error-table headers are generated artifacts but installed with public headers.
