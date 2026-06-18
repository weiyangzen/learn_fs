# File Research: sources/os/linux/linux/fs/xfs/scrub/health.h

Declares the scrub health-state helpers:
- `xchk_health_mask_for_scrub_type`
- `xchk_update_health`
- `xchk_ag_btree_del_cursor_if_sick`
- `xchk_mark_healthy_if_clean`
- `xchk_file_looks_zapped`
- `xchk_health_record`

This header exposes the bridge between scrub result flags and XFS health accounting.
