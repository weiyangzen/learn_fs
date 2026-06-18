# File Research: sources/os/linux/linux-stable/fs/nfs_common/nfsacl.c

Purpose: Encodes and decodes Solaris-style NFSv3 ACL protocol data to/from Linux POSIX ACLs.

Key responsibilities:
- Encodes ACL entries into XDR buffers or streams.
- Adds a Solaris-compatible ACL mask entry for minimal three-entry POSIX ACLs.
- Writes owner and owning group ids for `ACL_USER_OBJ` and `ACL_GROUP_OBJ`.
- Decodes XDR ACL arrays into `posix_acl`.
- Validates users, groups, permissions, tags, maximum entry count, and stream/buffer lengths.
- Sorts decoded ACL entries into canonical POSIX order.
- Removes bogus Solaris mask entries from minimal ACLs when mask permissions match group object permissions.

Integration:
- Exported to NFS client/server ACL protocol implementations.
- Uses generic SUNRPC XDR helpers and Linux POSIX ACL helpers.

Risks and notes:
- Encoding minimal ACLs uses a stack fake ACL to avoid allocation in fatal contexts.
- Decoder allocates ACL storage lazily on first decoded entry.
- Solaris interoperability drives several non-obvious transformations.
