# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_illegal.c

Purpose: provides dispatch handlers for illegal and unsupported NFSv4 operations.

Important APIs and types: uses `nfs_argop4`, `nfs_resop4`, `NFS4_OP_ILLEGAL`, `NFS4ERR_OP_ILLEGAL`, and `NFS4ERR_NOTSUPP`. Public handlers are `nfs4_op_illegal`, `nfs4_op_notsupp`, and their no-op free hooks.

Control flow: `nfs4_op_illegal` sets `resp->resop` to `NFS4_OP_ILLEGAL`, stores `NFS4ERR_OP_ILLEGAL` in the union's illegal status, emits a tracepoint, and returns `NFS_REQ_ERROR`. `nfs4_op_notsupp` sets `resp->resop` to the original `op->argop` so the response matches the unsupported operation number, stores `NFS4ERR_NOTSUPP` in the same union member, traces, and returns error.

State and persistence: no state, references, exports, filehandles, or persistent records are changed.

Dependencies and integration: used by the NFSv4 operation dispatch table for invalid opcodes or compiled/negotiated unsupported operations. Tracepoints provide lightweight observability.

Risks: the code relies on the response union layout using `opillegal.status` for unsupported operations. Dispatch table users must pick `illegal` versus `notsupp` correctly to preserve protocol-visible `resop`.

Test signals: invalid opcode maps to `OP_ILLEGAL`; known but unsupported opcode maps to original op number with `NFS4ERR_NOTSUPP`; free hooks are harmless.
