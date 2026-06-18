# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/health.h

This header declares scrub health integration helpers.

Exports:
- `xchk_health_mask_for_scrub_type`
- `xchk_update_health`
- `xchk_ag_btree_del_cursor_if_sick`
- `xchk_mark_healthy_if_clean`
- `xchk_file_looks_zapped`
- `xchk_health_record`

Purpose:
- Provides the interface for scrub modules to map scrub outcomes to incore XFS sick/healthy state.
- Also exposes cross-reference cursor pruning for already sick AG btrees.
