# File Research: sources/os/linux/linux/fs/nfsd/nfs2acl.c

Read completely: 389 lines.

NFSACL protocol version 2 procedure implementation, including ACL get/set plus getattr/access helpers and local XDR encode/decode/release logic.

Key responsibilities:
- Handles NULL, GETACL, SETACL, GETATTR, and ACCESS procedures for the NFSACL v2 side protocol.
- GETACL verifies the filehandle, validates the mask, obtains post attributes, returns access ACL or a mode-derived minimum ACL, and optionally returns default ACL.
- SETACL verifies setattr permission, takes write access, locks the inode, sets access and default POSIX ACLs, drops write access, and returns updated attributes.
- GETATTR and ACCESS reuse nfsd filehandle verification/access logic.
- Decodes v2 filehandles, ACL masks, POSIX ACL payloads, and access masks.
- Encodes status, attributes, ACL payloads, and access results; releases filehandles and POSIX ACL references.
- Publishes `nfsd_acl_version2` with procedure metadata, cache policy, XDR result sizing, dispatch, and per-CPU counters.

Dependencies:
- Uses POSIX ACL helpers, generic nfsd VFS helpers, legacy `linux/nfsacl.h`, and NFSv3 XDR helpers for shared ACL structures.

Notable risks:
- The file notes `nfsacl.h` is a broken header.
- GETACL/SETACL own several POSIX ACL references that must be released on all paths.
- Procedure name for ACLPROC2_ACCESS is set to `"SETATTR"`, which appears inconsistent with the operation.
