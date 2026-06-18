# File Research: sources/os/linux/linux-stable/fs/f2fs/iostat.h

## Purpose

`iostat.h` declares the F2FS iostat interface and provides no-op stubs when `CONFIG_F2FS_IOSTAT` is disabled. It defines latency classes, tunables, per-bio iostat context layout, and small inline helpers used by bio submission/completion paths.

## Main Contents

- `enum iostat_lat_type`
  - `READ_IO`
  - `WRITE_SYNC_IO`
  - `WRITE_ASYNC_IO`
  - `MAX_IO_TYPE`

- Iostat constants under `CONFIG_F2FS_IOSTAT`
  - `NUM_PREALLOC_IOSTAT_CTXS`: mempool size for bio contexts.
  - `DEFAULT_IOSTAT_PERIOD_MS`: default periodic trace interval.
  - `MIN_IOSTAT_PERIOD_MS`: minimum sysfs period.
  - `MAX_IOSTAT_PERIOD_MS`: maximum period, documented as one day.

- `struct iostat_lat_info`
  - `sum_lat[MAX_IO_TYPE][NR_PAGE_TYPE]`
  - `peak_lat[MAX_IO_TYPE][NR_PAGE_TYPE]`
  - `bio_cnt[MAX_IO_TYPE][NR_PAGE_TYPE]`

- `struct bio_iostat_ctx`
  - Stores the owning `f2fs_sb_info`.
  - Stores submit timestamp in jiffies.
  - Stores F2FS `enum page_type`.
  - Preserves `struct bio_post_read_ctx *` for read bios.

## Exported Interface

When enabled, the header declares:

- `iostat_info_seq_show()`
- `f2fs_reset_iostat()`
- `f2fs_update_iostat()`
- `f2fs_update_read_folio_count()`
- `iostat_update_and_unbind_ctx()`
- `iostat_alloc_and_bind_ctx()`
- `f2fs_init_iostat_processing()`
- `f2fs_destroy_iostat_processing()`
- `f2fs_init_iostat()`
- `f2fs_destroy_iostat()`

## Inline Helpers

- `iostat_update_submit_ctx()`
  - Assumes `bio->bi_private` points to `bio_iostat_ctx`.
  - Records `jiffies` and F2FS page type at submission.

- `get_post_read_ctx()`
  - Returns the saved post-read context from the wrapped bio private data.

## Disabled Build Behavior

When `CONFIG_F2FS_IOSTAT` is not set:

- Update and lifecycle routines compile to no-ops.
- Initialization returns success.
- `get_post_read_ctx()` returns `bio->bi_private` directly, preserving normal post-read behavior without iostat wrapping.

## Interactions

- Implemented by `iostat.c`.
- Used by data bio submission/completion paths.
- Depends on `NR_PAGE_TYPE`, `enum page_type`, `enum iostat_type`, and `struct f2fs_sb_info` definitions from core F2FS headers.
