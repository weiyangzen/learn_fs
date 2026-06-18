# File Research: sources/os/linux/linux/fs/coda/coda_linux.c

Linux/Coda translation helpers for FIDs, control names, open flags, inode attributes, and Coda vattrs.

Key functions:
- `coda_f2s()`: formats a Coda FID into a static string buffer.
- `coda_iscontrol()`: detects the special `.CONTROL` name.
- `coda_flags_to_cflags()`: maps Linux open flags to Coda open flags.
- `coda_inode_type()`: maps Coda vnode type to Linux inode file type.
- `coda_vattr_to_iattr()`: applies Coda attributes to Linux inode fields.
- `coda_iattr_to_vattr()`: initializes a Coda vattr with sentinel values, then maps Linux `iattr` fields marked valid.

Attribute behavior:
- Coda sentinel `-1` means “not provided / do not modify”.
- Size updates also set `i_blocks` as `(size + 511) >> 9`.
- Time conversion uses helpers between `coda_timespec` and `timespec64`.
- UID/GID conversion uses `init_user_ns`.

Other:
- Global `coda_fake_statfs` is defined here.
- `coda_f2s()` uses a static buffer, so it is not reentrant.
