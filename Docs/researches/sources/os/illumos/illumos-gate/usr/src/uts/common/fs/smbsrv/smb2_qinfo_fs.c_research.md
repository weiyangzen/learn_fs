# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_fs.c

Implements SMB2 filesystem information-class responses for `SMB2_0_INFO_FILESYSTEM`.

Key behavior:
- Dispatches volume, size, full size, device, attribute, control, object ID, and sector-size information.
- Disk-only classes validate `STYPE_ISDSK`; filesystem attributes can also describe IPC as `"PIPE"`.
- Reports disk filesystem name as `"NTFS"` for compatibility.
- Builds filesystem capabilities from tree flags, including Unicode-on-disk, ACLs, case sensitivity, named streams, quotas, and sparse files.
- Quota control information requires `SMB_TREE_QUOTA`, otherwise returns `NT_STATUS_VOLUME_NOT_UPGRADED`.
- Sector size information derives from `smb_fssize()` but clamps logical sector size with `smb2_max_logical_sector_size` for Hyper-V compatibility.

Important dependencies:
- `smb_fssize`, `smb_tree_has_feature`, tree resource type and flags.
- `smb_mbc_encodef` for wire layouts.

Notable details:
- Object IDs and driver-path/volume-flags classes are not supported.
- Sector-size response reports aligned/no-seek-penalty flags and unknown alignment offsets.
