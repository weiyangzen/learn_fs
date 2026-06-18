# sources/user-network-fs/samba/source4/dsdb/repl/drepl_fsmo.c

Purpose: handles IRPC requests to take FSMO roles by forwarding the appropriate DRS extended operation to the current role owner.

Important APIs/functions: `drepl_take_FSMO_role()` is the IRPC handler. It uses `dsdb_get_fsmo_role_info()` to find the FSMO object and owner NTDS DSA, maps `enum drepl_role_master` to `DRSUAPI_EXOP_FSMO_REQ_ROLE`, `DRSUAPI_EXOP_FSMO_RID_REQ_ROLE`, or `DRSUAPI_EXOP_FSMO_REQ_PDC`, checks whether this DC already owns the role with `samdb_dn_is_our_ntdsa()`, then calls `drepl_request_extended_op()`. `drepl_role_callback()` sets the output `WERROR` and sends the deferred IRPC reply.

Control flow/state: successful scheduling marks the IRPC message deferred; completion happens asynchronously after the DRS pull/extended op finishes. No local directory write is performed directly here; role changes are mediated by remote DRS behavior and later replication/application.

Dependencies/integration: DREPL IRPC registration in `drepl_service.c`, DSDB FSMO role utilities, extended operation scheduler, and tevent queue processing. Risks include trusted-IRPC panic for impossible role values, failure to identify current owner, and asynchronous failure propagation only through `out.result`. Test signals: already-owned roles return `WERR_OK`, each role maps to the correct exop, failed scheduling replies synchronously, and successful scheduling defers then replies from callback.
