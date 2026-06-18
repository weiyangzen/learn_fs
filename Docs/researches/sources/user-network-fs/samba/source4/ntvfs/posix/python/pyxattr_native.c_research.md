# sources/user-network-fs/samba/source4/ntvfs/posix/python/pyxattr_native.c

Purpose: `pyxattr_native.c` exposes a small Python extension module, `samba.xattr_native`, for direct filesystem extended attribute access. It is used by Samba Python tooling that needs to probe or manipulate native xattrs without going through the POSIX EADB emulation layer.

Important APIs, types, and functions: The module exports `wrap_getxattr(filename, attribute)`, `wrap_setxattr(filename, attribute, value)`, and `is_xattr_supported()`. Internally it uses Python argument parsing, `DATA_BLOB`, `getxattr`, `setxattr`, talloc temporary allocation, and the Samba Python module init macro.

Control flow: `is_xattr_supported` is a compile-time feature check around `HAVE_XATTR_SUPPORT`. `wrap_setxattr` parses two strings and a Python bytes buffer, then calls `setxattr` with flags 0. `wrap_getxattr` first calls `getxattr` with a NULL buffer to discover length, allocates a talloc buffer, calls `getxattr` again, and returns bytes.

State and persistence behavior: The module does not keep process state. Persistence is delegated to the host filesystem xattr implementation. Temporary buffers are freed before returning.

Dependencies and integration points: It depends on Python C API compatibility wrappers, Samba `DATA_BLOB`, talloc, `system/filesys.h`, and platform xattr functions. It is built as `samba/xattr_native.so` from the POSIX NTVFS build file.

Risks: The two-step get path has a normal race if the xattr changes between length discovery and read. It maps `ENOTSUP` to `IOError` and other failures to `OSError` with filename, so callers must handle platform-specific xattr errors. Zero-length xattrs allocate a zero-length talloc array and should be considered by tests.

Test signals: Useful tests import `samba.xattr_native`, check `is_xattr_supported`, set and get binary values, and validate expected exceptions on unsupported filesystems, missing files, and missing attributes.
