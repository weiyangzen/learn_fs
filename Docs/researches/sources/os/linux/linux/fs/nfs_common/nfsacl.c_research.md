# File Research: sources/os/linux/linux/fs/nfs_common/nfsacl.c

Implements encoding and decoding for the Solaris-style NFSv3 ACL protocol extension.

Key behavior:
- Documents the differences between Solaris NFS ACL wire format and Linux POSIX draft ACLs:
  - Minimal ACLs include a mask entry.
  - Minimal mask permissions match group object permissions.
  - Owner/group object IDs are encoded explicitly.
  - Wire ACL entries are unsorted.
- `xdr_nfsace_encode()` encodes one ACE as tag/typeflag, identifier, and permission bits, using inode owner/group for object entries.
- `nfsacl_encode()` writes ACL entry count and array data into an `xdr_buf`, inserting a synthetic mask entry for 3-entry minimal ACLs without allocating memory.
- `nfs_stream_encode_acl()` performs the same encoding through `xdr_stream`.
- `xdr_nfsace_decode()` allocates the POSIX ACL on first ACE decode, validates user/group IDs and permission bits, tolerates extra Solaris mask bits, and rejects unknown tags.
- `posix_acl_from_nfsacl()` sorts decoded ACEs and removes the synthetic mask from minimal ACLs when it matches group object permissions.
- `nfsacl_decode()` decodes from an `xdr_buf`, validates counts and converted POSIX form, returns decoded byte length, and optionally returns ACE count.
- `nfs_stream_decode_acl()` performs the same decode through `xdr_stream`.

Important interactions:
- Exported for NFS client and NFSD ACL procedure/XDR implementations.
- Uses init user namespace conversions, so ACL IDs are translated through kernel UID/GID helpers at encode/decode boundaries.
