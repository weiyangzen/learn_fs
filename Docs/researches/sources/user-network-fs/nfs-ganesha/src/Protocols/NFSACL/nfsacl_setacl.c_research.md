# sources/user-network-fs/nfs-ganesha/src/Protocols/NFSACL/nfsacl_setacl.c

Purpose: implements NFSACL SETACL, translating NFSv3 ACL wire structures into FSAL ACL attributes and applying them to an FSAL object.

Important APIs/types/functions: exports `nfsacl_setacl` and `nfsacl_setacl_Free`. It uses `nfs3_FhandleToCache`, `nfs3_acl_2_fsal_acl`, `nfs_get_grace_status`, `fsal_setattr`, FSAL `getattrs`, `fsal_release_attrs`, and `nfs_RetryableError`.

Control flow: the handler initializes response attributes as not-following, resolves the target handle, validates that an access ACL is present, rejects default ACLs on non-directories, converts access/default ACLs to `ATTR_ACL`, checks the grace-period gate, applies `fsal_setattr` with bypass semantics, fetches post-operation attributes, and maps success or FSAL errors to NFSv3 status.

State and persistence: this file mutates persistent file ACL metadata through FSAL `setattr`. It temporarily holds an FSAL object reference and an FSAL ACL attrlist that must be released to drop inherited ACL references.

Dependencies and integration points: tied to NFS server grace handling, FSAL ACL conversion, NFSv3 status mapping, and NLM share bypass comments. It uses NFSACL-specific result fields and NFSv3 attributes.

Risks and test signals: grace handling maps to `NFS3ERR_JUKEBOX`/drop behavior. A notable code path sets `res->res_getacl...attributes_follow` instead of the setacl result union after a successful getattrs, which deserves focused verification. Test directory and non-directory default ACLs, access ACL absence, FSAL setattr failure, grace period, retry/drop options, and returned post-op attributes.
