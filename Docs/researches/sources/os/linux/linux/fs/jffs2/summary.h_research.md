# File Research: sources/os/linux/linux/fs/jffs2/summary.h

## Role

Defines JFFS2 summary constants, on-flash summary record formats, in-memory summary record formats, and enabled/disabled summary APIs.

## Key Responsibilities

- Defines block-state constants returned by scan paths: all-FF, clean, partially dirty, cleanmarker-only, all-dirty, and bad block.
- Defines summary size macros for inode, dirent, xattr, and xref records.
- Defines `MAX_SUMMARY_SIZE`, `JFFS2_SUMMARY_NOSUM_SIZE`, and `JFFS2_SUMMARY_FRAME_SIZE`.
- Declares packed on-flash summary record structures and matching in-memory linked-list structures.
- Defines `struct jffs2_summary` for collected size/count/padding/list state and summary write buffer.
- Defines `struct jffs2_sum_marker`, stored at the end of summarized eraseblocks.
- Provides real prototypes under `CONFIG_JFFS2_SUMMARY` and no-op stubs otherwise.

## Important Interactions

- Included by scanner, allocator, direct-write, and write-buffer paths.
- Conditional stubs let callers invoke summary helpers without duplicating preprocessor checks.

## Invariants and Risks

- On-flash structures are packed and use endian-tagged JFFS2 integer types.
- Summaries larger than `MAX_SUMMARY_SIZE` are discarded.
- Disabled builds make `jffs2_sum_active()` false and all summary operations benign.
