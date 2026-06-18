# File Research: sources/os/linux/linux/fs/nfsd/vfs.h

`vfs.h` is the public internal header for NFSD VFS helpers implemented mainly in `vfs.c`. It defines permission/open flags, attribute wrapper state, the readdir callback type, and prototypes used by protocol operation handlers.

Important definitions:
- `NFSD_MAY_*` flags mirror Linux `MAY_EXEC`, `MAY_WRITE`, and `MAY_READ` for the low bits, then add NFSD-specific policy hints: setattr, truncation, NLM, owner override, local access, GSS bypass variants, lease-breaking suppression, read-if-exec, 64-bit readdir cookies, and localio tracing.
- `NFSD_MAY_CREATE` and `NFSD_MAY_REMOVE` combine the permission bits required for namespace mutation.
- `nfsd_filldir_t` is the callback ABI used by `nfsd_readdir()` to feed protocol-specific directory encoders.
- `struct nfsd_attrs` packages requested `iattr`, security label, POSIX access/default ACLs, and per-attribute error outputs.
- `nfsd_attrs_free()` releases ACL references; `nfsd_attrs_valid()` reports whether any regular attribute, label, or ACL update is pending.

The header declares lookup, setattr, create, access, open, read/write/commit, readlink/symlink/link/rename/unlink/readdir/statfs, permission, case-info, copy range, file close, and NFSv4-only fallocate/clone/xattr helpers. It is the main contract between NFSD protocol dispatch and the Linux VFS adaptation layer.
