<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/system.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/system.c

Source read: complete file, 114 lines, 3758 bytes, sha256 `00d3d9852cc33c76c5b5fd45dc60bcbe4f9b14036e1432904b481cb095279373`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/system.c_research.md`.

Purpose: portability wrappers for extended attribute operations used by dbench's optional DOS-attribute simulation. It normalizes Linux, BSD/extattr, and IRIX attr APIs behind three functions.

Important APIs/types/functions: `sys_getxattr(path, name, value, size)`, `sys_fgetxattr(fd, name, value, size)`, and `sys_fsetxattr(fd, name, value, size, flags)` dispatch to platform-specific xattr APIs when configured. It defines fallback `XATTR_CREATE` and `XATTR_REPLACE` constants when libc lacks Linux xattr headers.

Control flow: each wrapper uses preprocessor feature tests. Linux-style paths call `getxattr`, `fgetxattr`, or `fsetxattr`; BSD-style paths choose system/user namespace from the attribute prefix and strip text before the dot; IRIX-style paths map to `attr_get`, `attr_getf`, or `attr_setf`; unsupported platforms set `errno = ENOSYS` and fail.

State and persistence behavior: get calls only read metadata; `sys_fsetxattr()` persists extended-attribute values on an open file descriptor. State lives in the filesystem, not in process memory.

Dependencies and integration: included via `dbench.h`, which selects available xattr headers. `fileio.c` calls these wrappers when `options.ea_enable` is set to read/write `user.DosAttrib`.

Risks: IRIX branches assume attribute names contain a dot before taking `strchr(name, '.') + 1`; unsupported-platform failures can become fatal in `fileio.c` write hooks when xattrs are enabled. Namespace mapping based on `strncmp(name, "system", 6)` is coarse. Return semantics differ across OS APIs and are only lightly normalized.

Test signals: run dbench with extended attributes enabled on Linux/user-xattr, BSD/extattr, and unsupported filesystems. Verify expected failure handling for `ENOSYS`, permission-denied system namespaces, and successful read/write of `user.DosAttrib`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/system.c -->
