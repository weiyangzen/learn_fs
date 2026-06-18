# sources/user-network-fs/samba/source4/rpc_server/drsuapi/dcesrv_drsuapi.c

Purpose: main DRSUAPI DCE/RPC server endpoint for Active Directory replication management, bind negotiation, DC metadata queries, selected local operations, and forwarding of replication/KCC work to internal tasks.

Important APIs and control flow: binding requires privacy. `dcesrv_drsuapi_DsBind()` creates `drsuapi_bind_state`, opens samdb as system for DC callers or as user for others, optionally opens system context for RODC secret replication, discovers local site/config GUIDs and replication epoch, records remote bind data, builds local supported-extension info, and returns a DCE handle. `DsUnbind` frees that handle. Replica add/del/mod/sync and KCC/get-info operations enforce DC-level access then forward asynchronously via `dcesrv_irpc_forward_rpc_call()` to `dreplsrv` or `kccsrv`. `DsCrackNames` dispatches to name/list helper implementations for supported formats. `DsRemoveDSServer` validates and optionally deletes an `NTDS Settings` subtree. `DsGetDomainControllerInfo` searches Sites for server objects and composes level 1/2/3 DC info including computer, NTDS, site, PDC, GC, and RODC fields. Unsupported calls fault with operation-range errors through `DRSUAPI_UNSUPPORTED`.

State and persistence: bind handles own `drsuapi_bind_state` and samdb contexts. Writes are limited in this file to `DsRemoveDSServer`; many other mutating replication operations are forwarded.

Dependencies and integration: uses generated DRSUAPI server boilerplate, common SAM helpers, DRS utilities, DSDB/SAMDB search helpers, IRPC messaging, and security/session APIs.

Risks and test signals: access control and forwarding semantics are security-sensitive. Tests should cover bind extension negotiation by request length, DC/RODC/user samdb selection, privacy enforcement, async vs sync forwarding timeouts, DC info levels, malformed site DNs, unsupported op faults, and delete behavior with `commit` false/true.
