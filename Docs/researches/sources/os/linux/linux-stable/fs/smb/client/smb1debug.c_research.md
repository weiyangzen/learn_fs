# File Research: sources/os/linux/linux-stable/fs/smb/client/smb1debug.c

This small file provides SMB1-specific debug dumping through `cifs_dump_detail()`.

Behavior:
- Under `CONFIG_CIFS_DEBUG2`, it interprets the buffer as `struct smb_hdr` and logs command, CIFS error, flags, flags2, MID, PID, and word count.
- It then calls the server operation `check_message()` and, if the message validates, logs the calculated SMB size through `calc_smb_size()`.

Dependencies:
- Uses SMB1 protocol declarations from `smb1proto.h`, generic CIFS prototypes, and `cifs_debug.h`.
- The function is installed into `smb1_operations.dump_detail` in `smb1ops.c`.

Notes:
- With `CONFIG_CIFS_DEBUG2` disabled, the function is effectively a no-op.
