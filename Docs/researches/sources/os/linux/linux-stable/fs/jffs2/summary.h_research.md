# File Research: sources/os/linux/linux-stable/fs/jffs2/summary.h

This header defines JFFS2 summary constants, on-flash summary record formats, in-memory summary record formats, and summary API stubs/prototypes.

Key responsibilities:
- Defines block-state constants returned by scanner paths: all-FF, clean, partially dirty, cleanmarker-only, all-dirty, and bad-block.
- Defines summary size macros for inode, dirent, xattr, and xref records, plus `MAX_SUMMARY_SIZE` and `JFFS2_SUMMARY_NOSUM_SIZE`.
- Declares packed on-flash summary record structures and matching in-memory linked-list structures.
- Defines `struct jffs2_summary`, which tracks collected size/count/padding/list state and the summary write buffer.
- Defines `struct jffs2_sum_marker`, which stores the summary node offset and magic at the end of a summarized eraseblock.
- Exposes real summary functions when `CONFIG_JFFS2_SUMMARY` is enabled and no-op/stub forms when disabled.

Important interactions:
- Included by scanner, allocator, and write paths to coordinate summary collection and scan acceleration.
- Conditional stubs let the rest of JFFS2 call summary helpers unconditionally without spreading preprocessor logic through all call sites.

Notable invariants and risks:
- On-flash structures are packed and contain endian-tagged JFFS2 integer types.
- `MAX_SUMMARY_SIZE` is a hard allocation and usability boundary; larger summaries are intentionally discarded.
- Disabled builds make `jffs2_sum_active()` false and summary operations benign no-ops.
