# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getfh.c

Purpose: implements `GETFH`, returning the compound's current NFSv4 filehandle to the client.

Important APIs and types: uses `GETFH4res`, `nfs_fh4`, `fsal_attrlist`, and the current `compound_data_t` filehandle/object. It calls `nfs4_sanity_check_FH`, `check_resp_room`, `fs_supported_attrs`, `obj_ops->is_referral`, `nfs4_AllocateFH`, and `gsh_free`.

Control flow: the handler validates that a current filehandle exists and is usable, computes padded response size from `currentFH.nfs_fh4_len`, and checks available response room. It prepares a broad attr request from the FSAL supported attrs, excluding ACLs and FS locations, then asks the current object whether it is a referral. Referral filehandles return `NFS4ERR_MOVED` rather than exposing the handle. On success it allocates the result filehandle, copies length and bytes from `data->currentFH`, and returns `NFS4_OK`.

State and persistence: no persistent state changes. It allocates response memory that `nfs4_op_getfh_Free` releases on successful status.

Dependencies and integration: depends on compound filehandle state established by `PUTFH`, `PUTROOTFH`, `LOOKUP`, `OPEN`, or similar operations, plus FSAL referral detection and response sizing.

Risks: referral detection requires an attrlist and FSAL support; wrong masking could make referrals visible. The operation copies raw currentFH bytes, so preceding operations must have produced a valid handle. Error paths must set `data->op_resp_size` to just `nfsstat4`.

Test signals: no current FH, response too large, referral object returning `MOVED`, normal handle copy byte-for-byte, and result free.
