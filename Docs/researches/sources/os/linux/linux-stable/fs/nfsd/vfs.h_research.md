# File Research: sources/os/linux/linux-stable/fs/nfsd/vfs.h

Purpose: declares NFSD’s VFS helper API and permission flag vocabulary shared by NFSD protocol handlers, filecache, and VFS implementation code.

Key structures and state:
- Defines `NFSD_MAY_*` access bits for execute, write, read, setattr, truncate, lockd, owner override, local special-file access, GSS bypass hints, lease-breaking suppression, read-if-exec, 64-bit readdir cookies, and localio tracing.
- `NFSD_MAY_CREATE` and `NFSD_MAY_REMOVE` compose common directory mutation permission sets.
- Defines `nfsd_filldir_t`, the callback signature used by protocol-specific readdir encoders.
- `struct nfsd_attrs` bundles input `iattr`, security label, access/default POSIX ACLs, and output error slots for label/ACL application.
- Inline helpers release POSIX ACL references and test whether any attribute payload is present.

Major logic:
- Exposes errno translation, mount crossing, lookup, dentry lookup, setattr, mountpoint detection, create, access, commit, open, read, write, symlink, link, copy-file-range, rename, unlink, readdir, statfs, permission, and synchronous close helpers.
- Conditionally exposes NFSv4-only helpers for clone, fallocate, and xattr get/list/set/remove.
- Distinguishes high-level read/write wrappers from lower-level iterator/splice and already-open-file write helpers.

Concurrency and lifetime:
- API comments establish ownership expectations: many operations require callers to `fh_put()` involved filehandles, and attribute ACLs must be released with `nfsd_attrs_free()`.
- The declarations make filecache integration explicit through `struct nfsd_file` without exposing its layout.

Important dependencies:
- Includes Linux fs/POSIX ACL headers plus NFSD filehandle and core headers.
- Implemented primarily by `vfs.c` and called from NFSv2/v3/v4 procedure/XDR handling code.

Risk/edge cases:
- Permission flags intentionally alias low bits with `MAY_READ/WRITE/EXEC`; changing values would break `nfsd_permission()`.
- Some flags are hints for special NFS semantics rather than direct VFS permission bits, so callers must choose them carefully.
