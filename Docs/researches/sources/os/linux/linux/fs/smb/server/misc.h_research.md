# File Research: sources/os/linux/linux/fs/smb/server/misc.h

This header declares shared helper APIs for ksmbd utility code and procfs integration.

Functional areas:
- Filename and path handling: `match_pattern`, `ksmbd_validate_filename`, `parse_stream_name`, `convert_to_nt_pathname`, `convert_to_unix_name`, slash conversion helpers, and trailing-slash stripping.
- Share-name handling: `ksmbd_casefold_sharename` and `ksmbd_extract_sharename`.
- Directory response conversion: `ksmbd_convert_dir_info_name()` and `KSMBD_DIR_INFO_ALIGNMENT`.
- Time conversion: `NTFS_TIME_OFFSET`, `ksmbd_NTtimeToUnix`, `ksmbd_UnixTimeToNT`, and `ksmbd_systime`.

Procfs API:
- Under `CONFIG_PROC_FS`, declares `struct ksmbd_const_name` and proc helpers:
  `ksmbd_proc_init`, `ksmbd_proc_cleanup`, `ksmbd_proc_reset`, `ksmbd_proc_create`,
  `ksmbd_proc_show_flag_names`, and `ksmbd_proc_show_const_name`.
- Without procfs, init/cleanup/reset become no-op inline functions, keeping server lifecycle code simple.

Role in this group:
- `misc.c` implements the non-proc utility APIs.
- `proc.c` implements procfs setup and server counters.
- Session-management code implements some proc formatting helpers declared here, so this header is a shared contract across general server, session, connection, and file-cache instrumentation.
