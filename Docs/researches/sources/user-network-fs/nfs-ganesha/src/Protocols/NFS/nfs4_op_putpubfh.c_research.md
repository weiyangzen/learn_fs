# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_putpubfh.c

Purpose: implements `PUTPUBFH` by delegating to `PUTROOTFH`, effectively treating the public filehandle as the pseudo root.

Important APIs and types: uses `nfs4_op_putrootfh`, `PUTPUBFH` response union behavior, and no-op free hook.

Control flow: the handler calls `nfs4_op_putrootfh(op, data, resp)` to perform all work, then overwrites `resp->resop` with `NFS4_OP_PUTPUBFH` before returning the same request result.

State and persistence: same state effects as `PUTROOTFH`: current compound object/FH and export context are set to the pseudo root. No independent persistence or allocation occurs here.

Dependencies and integration: depends entirely on `nfs4_op_putrootfh` for access checks, root export lookup, filehandle creation, and error status population.

Risks: because it reuses the `PUTROOTFH` response union and only changes `resop`, callers must agree that status layout is compatible. If public FH semantics ever diverge from root FH semantics, this shortcut will need replacement.

Test signals: Pseudo root success via PUTPUBFH, access failures inherited from PUTROOTFH, and response `resop` reported as `NFS4_OP_PUTPUBFH`.
