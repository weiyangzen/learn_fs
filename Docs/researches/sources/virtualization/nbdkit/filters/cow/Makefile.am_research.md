# File Research: sources/virtualization/nbdkit/filters/cow/Makefile.am

Purpose: builds the copy-on-write filter and optional manual page.

Key details:
- Builds `nbdkit-cow-filter.la` from `blk.c`, `blk.h`, `cow.c`, and `cow.h`.
- Includes `common/bitmap`, `common/include`, `common/replacements`, and `common/utils`.
- Links bitmap, utility, replacement compatibility, and Windows import support.
- Applies shared filter version script when configured.
- Generates `nbdkit-cow-filter.1` from POD when available.

Integration notes:
- Unlike the cache filter, this filter supports persistent-in-process overlay state per export rather than a cache persistence policy.
