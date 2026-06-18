# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fsflush.c

## Role

Implements the `fsflush` kernel daemon that periodically writes old dirty filesystem data, scans pages for writeback/release, coalesces free pages, and triggers filesystem attribute sync.

## Main Behavior

- Global tunables `doiflush` and `dopageflush` control inode/attribute flushing and page flushing.
- `fsflush_iflush_delay` delays inode flushing after boot to reduce boot-time atime churn, except in single-user mode.
- `fsflush_do_pages()` scans a rotating subset of physical pages based on `t_fsflushr` and `v_autoup`.
- Dirty filesystem pages are detected with `hat_ismod()` or `hat_pagesync()` and written asynchronously with `VOP_PUTPAGE()`.
- Unmapped clean pages can be released with `page_release()`.
- Free adjacent pages are opportunistically promoted to larger page sizes using `page_promote_size()`.
- Maintains recent and cumulative scan statistics in `fsf_recent`, `fsf_total`, and `fsf_cycles`.

## Daemon Loop

- `fsflush()` initializes CPR state, waits on `fsflush_cv`, serializes reboot with `fsflush_sema`, then:
  - scans delayed-write buffer freelists and writes buffers older than `v_autoup`;
  - updates `bfreelist.b_bcount`;
  - calls `fsflush_do_pages()` if enabled;
  - periodically calls `fsop_sync_by_kind(..., SYNC_ATTR, ...)` across installed filesystems.

## Dependencies And Interactions

- Uses buffer cache lists, page/hat VM APIs, UFS buffer write path for UFS-backed delayed writes, and VFS switch iteration.
- Cooperates with CPR via `CALLB_CPR_*` and reboot serialization through `fsflush_sema`.
