# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_nverify.c

Purpose: implements NFSv4 `NVERIFY`, succeeding when supplied attributes do not match current object attributes and returning `NFS4ERR_SAME` when they do.

Important APIs and types: uses `NVERIFY4args/res`, `fattr4`, and `fsal_attrlist`. It calls `nfs4_sanity_check_FH`, `nfs4_Fattr_Check_Access`, `nfs4_Fattr_Supported`, `bitmap4_to_attrmask_t`, `file_To_Fattr`, `nfs4_Fattr_cmp`, and `nfs4_Fattr_Free`.

Control flow: validates current FH, rejects attributes that are not client-readable, rejects unsupported attributes, translates the requested bitmap to an FSAL attr request mask, and fetches current attributes through `file_To_Fattr`. It compares the client-provided fattr against freshly encoded file attributes. If the comparison says unequal, `NFS4_OK` is returned; if equal, the operation returns `NFS4ERR_SAME`; if comparison detects invalid data, it returns `NFS4ERR_INVAL`.

State and persistence: read-only. It allocates temporary fattr memory for current attrs and releases it before returning. It does not change compound current FH.

Dependencies and integration: shares attribute conversion and comparison code with VERIFY/GETATTR paths and depends on FSAL attr retrieval through `file_To_Fattr`.

Risks: on early `file_To_Fattr` errors the prepared attrs are not released in the visible code path, so attr masks with inherited allocations should be examined. Correct semantics depend on `nfs4_Fattr_cmp` returning false for not-same, true for same, and -1 for invalid.

Test signals: unreadable attrs, unsupported attrs, bitmap conversion failure, unequal attributes returning OK, equal attributes returning SAME, invalid encoded attr returning INVAL, and temporary fattr cleanup.
