# File Research: sources/os/linux/linux-stable/fs/smb/client/reparse.h

This header exposes CIFS reparse-point helpers and small inline conversions used by both SMB1 and SMB2/3 client paths.

Key contents:
- `REPARSE_SYM_PATH_MAX` defines the native symlink target limit used by `reparse.c`.
- `IO_REPARSE_TAG_INTERNAL` is a CIFS-only sentinel for cases where a reparse point is known from attributes but its data cannot be fetched.
- `reparse_mkdev()` decodes WSL `$LXDEV` major/minor encoding into Linux `dev_t`.
- `wsl_make_kuid()` and `wsl_make_kgid()` convert WSL EA uid/gid values into kernel ids, honoring mount-level uid/gid override flags.
- `reparse_mode_nfs_type()` maps Linux mode file types to NFS reparse inode types.
- `reparse_mode_wsl_tag()` maps Linux mode file types to WSL/LX reparse tags.

Important inode-cache logic:
- `reparse_inode_match()` matches cached reparse inodes by reparse tag and ctime. It deliberately skips strict tag matching when the cached tag is `IO_REPARSE_TAG_INTERNAL`, because the client cannot fetch the reparse data in that mode.
- `cifs_open_data_reparse()` normalizes open-info data so either POSIX info or SMB2 all-info carries `ATTR_REPARSE_POINT` when `data->reparse_point` is set.

Exported interfaces:
- `cifs_reparse_point_to_fattr()`
- `create_reparse_symlink()`
- `mknod_reparse()`
- `smb2_get_reparse_point_buffer()`

Dependencies:
- Includes CIFS global structures, mount context data, Linux uid/gid helpers, and common SMB FSCTL reparse definitions.
