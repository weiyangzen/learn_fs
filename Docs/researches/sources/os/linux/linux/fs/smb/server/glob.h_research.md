# File Research: sources/os/linux/linux/fs/smb/server/glob.h

This server-global header defines common KSMBD debug and allocation helpers.

Key contents:
- Includes Unicode and VFS cache headers.
- Declares global `ksmbd_debug_types`.
- Defines debug category bits for SMB, auth, VFS, oplock, IPC, connection, and RDMA.
- Sets `pr_fmt` to prefix messages with `ksmbd` and optional `SUBMOD_NAME`.
- `ksmbd_debug(type, ...)` emits `pr_info()` when the selected category bit is enabled.
- Defines `UNICODE_LEN(x)` and `KSMBD_DEFAULT_GFP`.

Many files in this group use `KSMBD_DEFAULT_GFP` and category debug logging from here.
