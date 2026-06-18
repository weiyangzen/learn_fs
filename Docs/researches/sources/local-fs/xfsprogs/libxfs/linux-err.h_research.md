# File Research: sources/local-fs/xfsprogs/libxfs/linux-err.h

Userspace adaptation of Linux error-pointer helpers.

Key responsibilities:
- Defines `MAX_ERRNO`, `IS_ERR_VALUE`, `ERR_PTR`, `PTR_ERR`, `IS_ERR`, `IS_ERR_OR_NULL`, `ERR_CAST`, and `PTR_ERR_OR_ZERO`.

Dependencies:
- Used by userspace ports of kernel code that return encoded error pointers.

Notable risks:
- Assumes Linux-style high-address error pointer encoding is acceptable in userspace.
