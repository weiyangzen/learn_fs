# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getattr.c

Purpose: implements NFSv4 `GETATTR` by translating a requested bitmap into FSAL attributes and encoding an NFSv4 `fattr4` result.

Important APIs and types: uses `GETATTR4args`, `GETATTR4res`, `fattr4`, `attrmask_t`, `fsal_attrlist`, and `nfs_client_id_t`. It calls `nfs4_sanity_check_FH`, `nfs4_Fattr_Check_Access_Bitmap`, `bitmap4_to_attrmask_t`, `nfs4_bitmap4_Remove_Unsupported`, `file_To_Fattr`, `nfs4_Fattr_Fill_Error`, `check_resp_room`, and delegation helpers `is_write_delegated` and `handle_deleg_getattr`.

Control flow: after current filehandle validation, empty bitmaps return success immediately. The handler rejects requests containing attributes not readable by clients, translates the bitmap to an attrmask, prepares FSAL attrs, and strips unsupported bitmap bits. For regular files, it checks write delegations under `STATELOCK_lock`; if another client holds a write delegation it invokes `handle_deleg_getattr`, allowing callback-based attribute refresh or returning delay/error. It then calls `file_To_Fattr`. Referral objects get special handling: if `fs_locations` or `rdattr_error` is requested, it fills restricted attrs and `NFS4ERR_MOVED`; otherwise it returns `NFS4ERR_MOVED`. On success it computes response size from the encoded attr list and verifies compound response room.

State and persistence: does not create persistent state, but it may trigger delegation callback behavior and consumes/refcounts a delegation client. It allocates fattr buffers that `nfs4_op_getattr_Free` releases on success and that the error path frees explicitly.

Dependencies and integration: depends on FSAL attr conversion, referral handling, mount-on fileid helpers, state/delegation code, compound response sizing, and LTTng tracepoints.

Risks: GETATTR sits on hot paths and must avoid leaking attr buffers on errors. Delegation callback behavior can introduce delay and must not hold the state lock across slow paths incorrectly. Referral behavior depends on exact requested bitmap semantics.

Test signals: empty bitmap success, unsupported/read-protected attributes, regular file attrs, referral with and without `RDATTR_ERROR`, response-size overflow, write delegation held by same client versus different client, and cleanup after `file_To_Fattr` failure.
