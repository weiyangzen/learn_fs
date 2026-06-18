# File Research: sources/local-fs/ntfs-3g/libntfs-3g/debug.c

## Role

Provides debug-only runlist dumping when `DEBUG` is enabled.

## Main Function

- `ntfs_debug_runlist_dump()` logs each runlist element as VCN, LCN, and length until the zero-length terminator.

## Dependencies

Uses `types.h`, `runlist.h`, `debug.h`, and `logging.h`.

## Important Behavior

Negative LCN sentinel values are rendered as symbolic labels for known runlist states such as `LCN_HOLE`, `LCN_RL_NOT_MAPPED`, `LCN_ENOENT`, and `LCN_EINVAL`; unknown negative values use a fallback label.

## Research Notes

This file has no runtime effect unless compiled with `DEBUG`. It is diagnostic support for metadata/runlist-heavy files such as `compress.c`, `attrib.c`, and allocation code.
