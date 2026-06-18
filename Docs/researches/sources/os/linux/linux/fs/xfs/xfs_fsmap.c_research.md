# File Research: sources/os/linux/linux/fs/xfs/xfs_fsmap.c

Implements `GETFSMAP`, translating XFS reverse/free-space metadata into generic `struct fsmap` records for userspace.

Key logic:
- Conversion helpers translate between public byte-addressed `fsmap` and internal basic-block `xfs_fsmap`.
- Owner conversion maps public special owners to rmap owners and vice versa.
- `struct xfs_getfsmap_info` holds query state: output head, record buffer, current AGF/group, next expected address, high/low rmap keys, missing-owner policy, device id, and last-record state.
- `xfs_getfsmap_helper` formats mappings, synthesizes gaps, counts records in count-only mode, checks shared extents through refcountbt when applicable, filters records before the continuation start, and marks flags such as prealloc, attr fork, extent map, and shared.
- Data device paths:
  - `__xfs_getfsmap_datadev` splits filesystem-wide keys into per-AG rmap/bnobt keys, iterates AGs, reads AGF, invokes a query function, and emits final gaps.
  - `xfs_getfsmap_datadev_rmapbt` uses rmapbt for privileged full mapping.
  - `xfs_getfsmap_datadev_bnobt` uses bnobt free-space records for fallback free/unknown ownership view.
- Log device path:
  - `xfs_getfsmap_logdev` fabricates a single log-owned mapping for an external log.
- Realtime paths under `CONFIG_XFS_RT`:
  - `xfs_getfsmap_rtdev_rtbitmap` reports free extents from the realtime bitmap.
  - `xfs_getfsmap_rtdev_rmapbt` reports full realtime mappings from rtrmapbt and handles zoned internal realtime volume offset padding.
- Device handling:
  - `xfs_getfsmap_device` returns synthetic internal device ids or encoded block-device ids.
  - `xfs_getfsmap_is_valid_device` and `xfs_getfsmap_check_keys` validate user query ranges.
- `xfs_getfsmap` configures handlers for data/log/realtime devices, chooses rmapbt only when the filesystem has rmapbt and the caller has `CAP_SYS_ADMIN`, sorts devices, iterates handlers, and sets output flags.
- `xfs_ioc_getfsmap` copies the userspace header, validates reserved fields, allocates an internal buffer up to 128 KiB with page fallback, loops to fill the caller’s record array, copies records out between lock-held queries, advances the low key using the last record, and sets `FMR_OF_LAST`.

The implementation’s subtlety is continuation semantics: physical keys are advanced for unshareable mappings, file offsets are advanced for shareable file data, and synthesized gaps must not duplicate or skip records.
