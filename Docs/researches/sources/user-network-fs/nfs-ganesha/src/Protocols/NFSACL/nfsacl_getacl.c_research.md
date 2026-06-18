# sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/nfsacl_getacl.c

Purpose: implements NFSACL GETACL for NFSv3-style POSIX ACL retrieval when `USE_NFSACL3` is compiled in.

Important APIs/types/functions: exports `nfsacl_getacl` and `nfsacl_getacl_Free`. It uses `nfs3_FhandleToCache`, FSAL `getattrs`, `fsal_acl_2_posix_acl`, POSIX `acl_valid`, `encode_posix_acl`, `nfs3_Fixup_FSALattr`, `fsal_release_attrs`, and `nfs_RetryableError`.

Control flow: it prepares NFSv3 ACL attributes, resolves the file handle to an FSAL object, fetches attributes/ACL, validates the caller mask against allowed ACL bits, optionally encodes access and default ACLs, fixes returned attributes, sets `NFS3_OK`, and releases all object/ACL references. Failures map FSAL status to NFSv3 status and may return `NFS_REQ_DROP` for retryable errors.

State and persistence: no persistent mutation. It allocates encoded ACL buffers into the result and obtains temporary POSIX ACLs that are freed before return. It also fetches attributes whose embedded references are released.

Dependencies and integration points: bridges NFSACL wire masks (`NFS_ACL`, `NFS_ACLCNT`, `NFS_DFACL`, `NFS_DFACLCNT`) with FSAL ACL storage and NFSv3 post-op attributes. It depends on the helper conversions in `nfs_proto_tools.c`.

Risks and test signals: invalid masks, missing ACLs, invalid POSIX ACLs, and retryable FSAL failures are key branches. Result free currently does nothing, so ownership of encoded ACL result storage should be checked against the generated XDR free path. Test access/default ACL retrieval for files and directories, empty ACLs, invalid masks, stale handles, and FSAL transient errors.
