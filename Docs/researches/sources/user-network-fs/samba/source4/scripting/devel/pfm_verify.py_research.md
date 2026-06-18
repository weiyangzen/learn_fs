<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/pfm_verify.py -->
# sources/user-network-fs/samba/source4/scripting/devel/pfm_verify.py

Purpose: verifies that a server's cached DRS prefixMap and schemaInfo match the values stored in the Schema naming context.

Important APIs/types/functions: `_samdb_fetch_pfm`, `_samdb_fetch_schi`, `_drs_fetch_pfm`, `_pfm_verify`, `_pfm_schi_verify`, `DsGetNCChangesRequest8`, `drsblobs.prefixMapBlob`, `schemaInfoBlob`, and DRS mapping counters.

Control flow: parses server and credentials, falls back to `DC_SERVER`, opens LDAP SamDB, fetches prefixMap/schemaInfo over DRS with `max_object_count=0`, removes the schemaInfo pseudo mapping from the DRS mapping counter, fetches LDB-stored prefixMap/schemaInfo, compares count, prefix IDs, OID lengths/binary OIDs, marker, revision, and invocation ID, and exits 1 or 2 on mismatches.

State and persistence behavior: read-only LDAP and DRS queries.

Dependencies and integration points: combines DRS replication wire mapping data with schema NC attributes. Useful for diagnosing schema replication/cache correctness.

Risks: uses `str(res[0]['prefixMap'])` and `str(schemaInfo)` for NDR input, which can be fragile if the binding expects bytes. Assertions can abort without clean diagnostics. Hardcoded destination DSA GUID is artificial.

Test signals: zero exit means prefixMap and schemaInfo match. Exit 1 indicates prefixMap mismatch; exit 2 indicates schemaInfo mismatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/pfm_verify.py -->
