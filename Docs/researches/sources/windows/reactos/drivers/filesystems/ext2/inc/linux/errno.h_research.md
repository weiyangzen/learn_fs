# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/errno.h

This header maps Linux errno values into the compatibility layer.

Behavior:
- Includes host `<errno.h>`.
- For non-ReactOS builds, defines the common Linux errno range from `EPERM` through many network/library errors.
- Some values are defined unconditionally even on ReactOS, including `ENODATA`, `EBADMSG`, `EMSGSIZE`, `EOPNOTSUPP`, network/socket errors from `EADDRINUSE` onward, quota/media errors, internal restart/ioctl codes, and NFSv3-related errors.

Role:
- Lets Linux-derived ext2/ext3/ext4/JBD code return expected negative errno values before conversion through `Ext2WinntError`/`Ext2LinuxError`.

Notable risk:
- Conditional definition avoids clashes with ReactOS for many values but still defines others unconditionally, so compatibility depends on existing system errno headers not defining conflicting macros.
