# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_mount.h

Read completely: 63 lines.

Defines the user/kernel mount argument ABI for NetBSD UDF. `struct udf_args` carries the version, device specifier, session selector, mount flags, GMT offset, uid/gid mapping parameters for anonymous and nobody ownership, an explicit sector size for dump/file mounts, and reserved space for future extension.

The only mount flag defined here is `UDFMNT_CLOSESESSION`, exposed with `UDFMNT_BITS` for flag decoding. `UDFMNT_VERSION` is currently `1`.

Risk is ABI compatibility: this structure is passed across the mount interface, so field ordering, sizes, and reserved space matter for old userland/new kernel interactions.
