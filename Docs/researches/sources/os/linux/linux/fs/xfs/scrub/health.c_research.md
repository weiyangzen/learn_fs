# File Research: sources/os/linux/linux/fs/xfs/scrub/health.c

Maps scrub results to XFS in-core health state. Scrub and repair can perform cross-structure validation, so this file updates filesystem, AG, inode, and realtime-group sickness flags based on scrub outcomes.

Main components:
- `enum xchk_health_group` identifies whether a scrub type maps to no object, filesystem, AG, inode, or realtime group health.
- `type_to_health_flag` maps each scrub type to its health group and sickness mask.
- `xchk_health_mask_for_scrub_type` returns the default sickness mask.
- `xchk_mark_healthy_if_clean` adds extra health bits to clear if the scrub result stayed clean.
- `xchk_file_looks_zapped` detects pre-existing zapped inode metadata while allowing post-repair revalidation.
- `xchk_mark_all_healthy` clears indirect filesystem, AG, and realtime-group health markers after a clean whole-filesystem health scan.
- `xchk_update_health` is the central updater. It sets direct sickness flags on corrupt results and clears masks on clean results, with special handling for repair and the `HEALTHY` scrub type.
- `xchk_ag_btree_del_cursor_if_sick` discards cross-reference cursors for known-sick AG btrees, setting `XFAIL` instead of trusting them.
- `xchk_health_record` checks for any remaining primary sickness in filesystem, AG, or realtime-group health records.

Key policy:
- Runtime errors do not update health.
- Clean scans clear the relevant sick flags.
- Corrupt scans set them.
- Repairs that rebuild multiple structures must expand the sick mask so all rebuilt structures are revalidated and updated together.
