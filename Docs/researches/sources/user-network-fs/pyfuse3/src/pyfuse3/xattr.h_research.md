# sources/user-network-fs/pyfuse3/src/pyfuse3/xattr.h

Purpose: Provides platform-independent wrappers for extended attribute get/set operations and normalizes missing constants across Linux, BSD, and Darwin.

Important APIs/types/functions: Defines `UNUSED`, maps Linux `ENOATTR` to `ENODATA` when needed, stubs namespace/flag constants on Linux/Darwin, defines BSD `XATTR_CREATE`/`XATTR_REPLACE` as zero, and provides static `getxattr_p`/`setxattr_p` wrappers for each platform.

Control flow: Compile-time platform branches select system headers and wrapper implementations. BSD wrappers check `size >= SSIZE_MAX`, map extattr APIs, and validate full writes.

State and persistence: No state; wrappers operate on filesystem paths and xattr buffers.

Dependencies and integration points: Used by native pyfuse3 extension code for `pyfuse3.getxattr`/`setxattr` behavior. Depends on system xattr/extattr APIs.

Risks: BSD lacks create/replace semantics in this wrapper, so tests for those flags cannot be positive. Linux wrapper ignores namespace argument because Linux encodes namespace in the attribute name. Path-based xattr APIs can race with filesystem changes.

Test signals: `test_api.py::test_xattr` compares pyfuse3 xattr behavior with Python `os.getxattr`/`os.setxattr` where available and skips unsupported filesystems.
