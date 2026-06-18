# sources/user-network-fs/samba/source4/rpc_server/drsuapi/addentry.c

Purpose: implements the DRSUAPI `DsAddEntry` RPC, used by replication partners to add directory objects, including special handling for new `nTDSDSA` objects.

Important APIs and control flow: `dcesrv_drsuapi_DsAddEntry()` pulls the DRS bind handle, requires `SECURITY_DOMAIN_CONTROLLER`, starts an LDB transaction for level 2 requests, commits origin objects with `dsdb_origin_objects_commit()` using `DSDB_REPL_FLAG_ADD_NCNAME`, fills the level 3 reply, calls `drsuapi_add_SPNs()`, and commits or cancels on failure. `drsuapi_add_SPNs()` scans added objects for `objectClass=ntDSDSA`, follows `serverReference`, reads the NTDS object GUID and server computer `dNSHostName`/`cn`, then permissively adds replication and LDAP SPNs to the referenced machine account.

State and persistence: writes replicated objects and servicePrincipalName values to samdb inside one transaction. Reply state includes added object identifiers and error data.

Dependencies and integration: depends on DRS bind state, SAMDB/DSDB replication commit helpers, security checks, loadparm DNS domain, and generated DRSUAPI NDR.

Risks and test signals: transaction integrity is critical because SPN failure cancels the add. Tests should cover non-DC access denial, unsupported levels, origin object commit failures, nTDSDSA with/without serverReference, duplicate SPNs under permissive modify, and transaction rollback.
