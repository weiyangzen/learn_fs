# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/health.c

This file maps scrub results to XFS incore health state. It centralizes how online scrub and repair set or clear sick flags on filesystem, allocation group, inode, and realtime group objects.

Key data:
- `enum xchk_health_group` classifies a scrub type as filesystem-wide, AG, inode, rtgroup, or none.
- `type_to_health_flag` maps every `XFS_SCRUB_TYPE_*` to a sick-mask group and mask.

Main operations:
- `xchk_health_mask_for_scrub_type` returns the default sick mask for a scrub type.
- `xchk_mark_healthy_if_clean` adds extra flags to `healthy_mask` when scrub found no direct or cross-reference corruption.
- `xchk_file_looks_zapped` checks whether inode metadata appears previously zapped, except during post-repair revalidation.
- `xchk_update_health` applies scrub results:
  - corrupt/xcorrup shows as sick
  - clean clears `sick_mask | healthy_mask`
  - `HEALTHY` scrub clears indirect health flags after a clean full scan
  - inode repair requests add `XFS_SICK_INO_FORGET`
- `xchk_ag_btree_del_cursor_if_sick` drops cross-reference btree cursors if their known health is bad, setting `XFAIL`.
- `xchk_health_record` checks existing primary health flags across fs, AGs, and rtgroups and marks corruption if any remain.

Important invariants:
- Runtime scrub errors do not update health; only completed scrub results do.
- Repairers that rebuild multiple structures are expected to expand the sick mask.
- Cross-reference scans avoid relying on metadata already marked sick, except when scrubbing the same structure or revalidating freshly repaired AG metadata.

Risks and edge cases:
- Health state is intentionally conservative when repair is requested, to avoid stale inode sickness propagating after inactivation.
- `XFS_SCRUB_TYPE_HEALTHY` has special behavior because it clears indirect evidence, not one direct metadata type.
