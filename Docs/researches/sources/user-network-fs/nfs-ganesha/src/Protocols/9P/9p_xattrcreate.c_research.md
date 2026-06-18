## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_xattrcreate.c

Purpose: prepares a fid for extended-attribute creation/replacement/removal.

APIs and flow: `_9p_xattrcreate` validates fid, max xattr size, write access, and name length. Size zero maps to `remove_extattr_by_name`. Nonzero size allocates a fid xattr buffer, records expected size/name/write mode, optionally skips initial creation for POSIX ACL or overlong copied name, otherwise calls `setextattr_value` with create/replace semantics and retry-on-exists behavior for flag zero.

State/dependencies: stores deferred xattr content in `pfid->xattr`; actual final value is written during clunk after client writes the payload. Depends on FSAL xattr APIs and POSIX xattr flags.

Risks/tests: test create/replace/exclusive flags, size limit, remove path, POSIX ACL special case, write then clunk, size mismatch, and cleanup on FSAL create failure.
