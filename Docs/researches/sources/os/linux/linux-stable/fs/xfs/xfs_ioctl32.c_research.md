# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl32.c

This file implements 32-bit compat handling for XFS ioctls on 64-bit kernels. It translates compat userspace structures, pointer fields, alignment-sensitive layouts, and selected ioctl numbers into native XFS operations.

Major functionality:
- Alignment-specific helpers under `BROKEN_X86_ALIGNMENT`:
  - `xfs_compat_ioc_fsgeometry_v1` copies geometry into the packed 32-bit layout.
  - `xfs_compat_growfs_data_copyin` and `xfs_compat_growfs_rt_copyin` translate growfs requests.
  - `xfs_fsinumbers_fmt_compat` formats inode-group records into compat layout.
- Bulkstat compat:
  - `xfs_ioctl32_bstime_copyin`, `xfs_ioctl32_bstat_copyin`, and `xfs_bstime_store_compat` translate time/stat fields.
  - `xfs_fsbulkstat_one_fmt_compat` formats legacy `xfs_bstat` records for 32-bit userspace.
  - `xfs_compat_ioc_fsbulkstat` handles compat bulkstat, bulkstat single, and inumbers; x32 ABI is special-cased to use native output structure layout while keeping compat input pointers.
- Handle and attr-by-handle compat:
  - `xfs_compat_handlereq_copyin` translates embedded compat pointers.
  - `xfs_compat_attrlist_by_handle` and `xfs_compat_attrmulti_by_handle` enforce `CAP_SYS_ADMIN`, resolve handles, and invoke native attr list/multi operations with compat pointer conversion.
- Main dispatcher:
  - `xfs_file_compat_ioctl` maps compat commands to native helpers, directly handles commands whose structure layout differs, and falls back to `xfs_file_ioctl` for compatible commands.

Security and validation:
- Admin-only paths check `CAP_SYS_ADMIN`.
- Mutating operations acquire write access with `mnt_want_write_file`.
- Multi-attr operation count is overflow checked and capped to at most `16 * PAGE_SIZE`.
- All userspace pointers are converted through `compat_ptr`.

Notable implementation detail:
- `xfs_ioctl32_bstat_copyin` copies many individual `compat_xfs_bstat` fields. The source shows `bs_blocks` and `bs_xflags` being read from `bstat32->bs_size`, which is worth flagging for review because the surrounding field-by-field pattern suggests these should correspond to their own compat fields.

Integration:
- Calls native implementations from `xfs_ioctl.c`, handle helpers, attr helpers, growfs helpers, and itable formatting functions.
