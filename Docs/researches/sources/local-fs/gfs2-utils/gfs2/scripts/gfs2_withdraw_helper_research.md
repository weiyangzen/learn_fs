# File Research: sources/local-fs/gfs2-utils/gfs2/scripts/gfs2_withdraw_helper

Shell helper invoked by the GFS2 withdraw udev rule. It is not intended for manual use.

Behavior:
1. Validates udev environment: `SUBSYSTEM=gfs2`, `LOCKPROTO=lock_dlm`, nonempty `DEVPATH`, and `ACTION=offline`.
2. Builds `SYSFS_TOPDIR=/sys$DEVPATH`.
3. Reads device-mapper name from `$SYSFS_TOPDIR/device/dm/name`.
4. Builds `/dev/mapper/$DM_NAME`.
5. Attempts device suspension with `dmsetup suspend`.
6. If `$SYSFS_TOPDIR/lock_module/withdraw` exists, writes `1` to acknowledge withdraw completion.

Research notes:
- The test `if [ -z "$DM_DEV" ]` is suspicious because `DM_DEV` is assigned `/dev/mapper/$DM_NAME`, so it is normally nonempty even when `DM_NAME` is empty. That condition likely prevents suspension in normal cases.
