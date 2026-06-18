# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/util.h

This header declares shared fsck utility APIs and defines small inline bitmap/type helpers used across passes.

It exposes progress, query/input, duplicate-reference, directory hash, free-block, and pass-duration functions implemented in `util.c`. It also exports `reftypes[]` and duplicate-reference helpers used by duplicate-block resolution code.

Important inline helpers:
- `block_type()` decodes a two-bit fsck block-state map.
- `link1_type()` decodes a one-bit link bitmap.
- `link1_destroy()` frees one-bit bitmap storage.
- `bitmap_type()` reads the on-disk GFS2 resource-group bitmap state for a block.
- `block_type_string()` maps GFS2 block states to display strings.
- `is_dir()` wraps `S_ISDIR()` on `i_mode`.

The header depends on `fsck.h`, `libgfs2.h`, and system `stat` mode macros. It also defines `INODE_VALID`, `INODE_INVALID`, and a `stack` debugging macro that logs the current function.

Risks and notes:
- The inline bitmap helpers assume valid block indexes and initialized maps.
- `block_type()`/`link1_type()` use static locals, so they are not thread-safe, though fsck is effectively single-threaded.
