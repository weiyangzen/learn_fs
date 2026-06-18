# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_fsinfo.c

## Role

Implements SMB1 disk/filesystem information queries and filesystem control-info setting, including quota-aware capacity reporting.

## Major Responsibilities

- Handles legacy `SMB_COM_QUERY_INFORMATION_DISK`.
- Handles Trans2 query filesystem information levels for allocation, volume, size, device, attributes, control, and full-size information.
- Reports filesystem capabilities based on SMB tree features.
- Formats volume labels and filesystem names for Unicode and non-Unicode clients.
- Computes caller-visible capacity and free space using filesystem stats and optional per-user quota data.
- Handles Trans2 set filesystem control information for quota enforcement defaults.

## Key Functions

- `smb_com_query_information_disk()` returns old 16-bit disk capacity fields, scaling block/unit values to fit legacy clients.
- `smb_com_trans2_query_fs_information()` decodes the information level and encodes the requested FS structure.
- `smb_fssize()` calls `smb_fsop_statfs()`, normalizes block geometry, computes total/free units, and applies user quota limits when supported.
- `smb_com_trans2_set_fs_information()` dispatches supported set-info levels.
- `smb_trans2_set_fs_ctrl_info()` permits only administrators to set quota control info and only supports enforced quotas with unlimited defaults.

## Research Notes

The server reports the filesystem name as `NTFS` for compatibility while deriving feature flags from the share/tree state. Quota reporting affects caller-visible units but leaves volume-visible units available for full-size information.
