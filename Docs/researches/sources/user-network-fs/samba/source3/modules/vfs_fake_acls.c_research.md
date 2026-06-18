# sources/user-network-fs/samba/source3/modules/vfs_fake_acls.c

## Purpose
`vfs_fake_acls.c` stores fake uid/gid and POSIX ACL data in xattrs, letting tests exercise ACL/ownership behavior without relying on real filesystem metadata.

## Important APIs, Types, And Functions
The module uses xattrs `system.fake_uid`, `system.fake_gid`, `system.fake_access_acl`, and `system.fake_default_acl`. Stat wrappers overlay fake uid/gid. ACL helpers NDR-serialize `struct smb_acl_t` into xattrs. Chown wrappers write fake uid/gid xattrs. `fake_acl_process_chmod()` updates stored ACL entries to reflect chmod modes. `fake_acls_connect()` installs a recursion guard for pathref opening.

## Control Flow
Stat hooks delegate first, then read fake metadata from an fsp or open a pathref fsp to access xattrs. The pathref path uses a recursion guard because opening pathrefs may stat internally. ACL get grows a buffer until xattr retrieval succeeds, then decodes. ACL set encodes and writes. `fchmod` delegates real chmod first, then updates fake access ACL if present.

## State And Persistence
Fake metadata persists in filesystem xattrs. Memory state is limited to the per-handle recursion guard.

## Dependencies And Integration Points
The module uses Samba xattr hooks, pathref/filename conversion, NDR ACL definitions, POSIX ACL helpers, current uid helpers, and metadata fsp behavior.

## Risks
`system.*` xattrs may require privileges or be unsupported. `fake_acls_lchown()` appears to return positive `EACCES` instead of `-1` with errno. Some pathref failures are ignored by design for tests. ACL blobs are tied to Samba's NDR format. Real chmod still changes mode bits.

## Test Signals
Test fake uid/gid overlays, fstatat pathref behavior, recursion guard, absent/malformed xattrs, ACL set/get/delete, chmod ACL rewriting and mask creation, chown privilege checks, stream metadata, and xattr namespace failures.
