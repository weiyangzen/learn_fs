# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/udf_iconv.c

FreeBSD UDF iconv module registration shim.

Key responsibilities:
- Includes the kernel iconv, module, and mount headers needed for filesystem charset conversion registration.
- Invokes `VFS_DECLARE_ICONV(udf)` to expose UDF charset conversion hooks.

Dependencies:
- Depends on FreeBSD kernel iconv support and the VFS iconv registration macro.
- Used by UDF mount and vnode code through the external `udf_iconv` function table.

Notable risks:
- If kernel iconv support is unavailable or not loaded, UDF falls back to limited built-in Unicode-to-byte translation.
- This file only registers the hook; mount option validation and actual conversion behavior live elsewhere.
