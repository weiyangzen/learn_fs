# File Research: sources/os/linux/linux/fs/nfsd/nfs3acl.c

Read completely: 279 lines.

NFSACL protocol version 3 procedure implementation for POSIX ACL get/set over the NFSv3 ACL side protocol.

Key responsibilities:
- Handles NULL, GETACL, and SETACL procedures.
- GETACL verifies the filehandle, validates the requested ACL mask, returns access ACL or a mode-derived minimum ACL, and optionally returns default ACL.
- SETACL verifies setattr permission, takes write access, locks the inode, sets access and default POSIX ACLs, and returns post-op attributes.
- Decodes NFSv3 filehandles, masks, and ACL payloads.
- Encodes NFSv3 status, post-op attributes, ACL masks, ACL payloads, and SETACL post-op attributes.
- Releases filehandle and POSIX ACL references.
- Publishes `nfsd_acl_version3` with procedure table, dispatch, XDR sizing, and per-CPU counters.

Dependencies:
- Shares data structures and XDR helpers with NFSv3 server code and legacy NFSACL support.

Notable risks:
- SETACL stores raw `nfserrno(error)` after the drop-lock label; if both ACL updates succeed, `error` is zero, which maps to success as intended.
- Default ACL handling for non-directories is left to filesystem/POSIX ACL behavior.
