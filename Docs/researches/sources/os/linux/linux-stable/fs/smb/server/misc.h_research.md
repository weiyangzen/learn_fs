# File Research: sources/os/linux/linux-stable/fs/smb/server/misc.h

This header declares common ksmbd helper APIs implemented by `misc.c` and, under `CONFIG_PROC_FS`, proc helper APIs implemented by `proc.c`.

Declared utility APIs:
- Pattern and filename parsing:
  - `match_pattern()`
  - `ksmbd_validate_filename()`
  - `parse_stream_name()`
- Path conversion:
  - `convert_to_nt_pathname()`
  - `ksmbd_conv_path_to_unix()`
  - `ksmbd_strip_last_slash()`
  - `ksmbd_conv_path_to_windows()`
  - `ksmbd_casefold_sharename()`
  - `ksmbd_extract_sharename()`
  - `convert_to_unix_name()`
- Metadata formatting:
  - `get_nlink()`
  - `ksmbd_convert_dir_info_name()`
- Time conversion:
  - `NTFS_TIME_OFFSET`
  - `ksmbd_NTtimeToUnix()`
  - `ksmbd_UnixTimeToNT()`
  - `ksmbd_systime()`

Proc-related definitions under `CONFIG_PROC_FS`:
- `struct ksmbd_const_name`
- `ksmbd_proc_init()`
- `ksmbd_proc_cleanup()`
- `ksmbd_proc_reset()`
- `ksmbd_proc_create()`
- `ksmbd_proc_show_flag_names()`
- `ksmbd_proc_show_const_name()`

No-proc stubs:
- If `CONFIG_PROC_FS` is disabled, init/cleanup/reset become no-op inline functions.

Role:
- Shared interface for protocol handlers, VFS helpers, share handling, and optional proc reporting.

Risk areas:
- The proc helper declarations are only available under `CONFIG_PROC_FS`; code using `ksmbd_proc_create()` or proc format helpers must be similarly guarded or conditionally compiled.
