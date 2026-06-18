# File Research: sources/os/linux/linux-stable/fs/gfs2/util.h

## Scope

This header provides GFS2 logging macros, assertion/consistency/error macros, metadata validation helpers, freeze/withdraw declarations, cache externs, and tunable access helpers.

## APIs And Definitions

- `fs_emerg`, `fs_warn`, `fs_err`, and `fs_info` prefix messages with `fsid=<sd_fsname>`.
- `gfs2_assert()` BUGs on fatal assertions; `gfs2_assert_withdraw()` logs and withdraws; `gfs2_assert_warn()` rate-limited warns and returns whether the assertion failed.
- `gfs2_consist()`, `gfs2_consist_inode()`, and `gfs2_consist_rgrpd()` wrap consistency reporting with caller location.
- `gfs2_meta_check()` checks only GFS2 magic and returns `-EIO`; `gfs2_metatype_check()` checks magic and expected metadata type and reports failures through withdrawing helpers.
- `gfs2_metatype_set()` writes type and format into a metadata header.
- I/O error macros wrap block/non-block error reporting.
- `gfs2_tune_get()` reads a tunable under `gt_spin`.
- `gfs2_withdrawn()` tests `SDF_WITHDRAWN` with an unlikely branch hint.
- Externs expose all major GFS2 slab caches and the page mempool.

## Dependencies And Invariants

The metadata helpers assume buffer data starts with `struct gfs2_meta_header`. `gfs2_tune_get()` is a snapshot and does not keep the tunable stable after return. Consistency macros are intended for serious on-disk or internal invariants; many call sites withdraw rather than attempting recovery in-place.
