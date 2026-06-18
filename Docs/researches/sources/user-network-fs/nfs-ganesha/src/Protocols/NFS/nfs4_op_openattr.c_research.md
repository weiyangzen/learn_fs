# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_openattr.c

Purpose: provides the `OPENATTR` operation hook, but the operation is not implemented.

Important APIs and types: uses `OPENATTR4args`, `OPENATTR4res`, and `nfs_resop4`. The only public behavior is `nfs4_op_openattr`, with `nfs4_op_openattr_Free` as a no-op.

Control flow: the handler sets `resp->resop = NFS4_OP_OPENATTR`, unconditionally sets `res_OPENATTR4->status = NFS4ERR_NOTSUPP`, and returns `NFS_REQ_ERROR`. It does not inspect the target filehandle or the OPENATTR arguments beyond taking the union address.

State and persistence: no state changes, no filesystem operations, no allocations.

Dependencies and integration: used by the NFSv4 operation dispatch table to advertise a defined but unsupported operation. It depends only on core NFSv4 response types.

Risks: clients expecting named attribute directories receive `NOTSUPP`. Because no FH sanity check is performed, the unsupported status takes precedence over filehandle errors; this should match intended protocol behavior for unsupported ops.

Test signals: any OPENATTR request returns `NFS4ERR_NOTSUPP`; free hook is harmless; compound stops with `NFS_REQ_ERROR`.
