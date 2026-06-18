# File Research: sources/local-fs/ocfs2-tools/include/tools-internal/Makefile

## Purpose

Build/install metadata for internal ocfs2-tools support headers.

## Main Contents

- Includes top-level preamble/postamble.
- Lists internal headers: `verbose.h`, `progress.h`, `utils.h`, and `scandisk.h`.
- Adds these headers to `DIST_FILES`.

## Dependencies and Integration

- Does not define installed public header metadata, implying these are distribution/internal headers rather than libocfs2 public API.
