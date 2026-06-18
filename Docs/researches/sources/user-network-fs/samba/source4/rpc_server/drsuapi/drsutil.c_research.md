# sources/user-network-fs/samba/source4/rpc_server/drsuapi/drsutil.c

Purpose: shared DRS server utilities for controlled LDB searches, caller authorization, secret attribute filtering, and extended-right access checks.

Important APIs and control flow: `drsuapi_search_with_extended_dn()` builds a search request manually, adds extended-DN, show-recycled, and reveal-internals controls, waits synchronously, and returns the result under the caller context. `drs_security_level_check()` optionally honors `drs:disable_sec_check`, otherwise compares the session security level against a required minimum and logs refused tokens. `drsuapi_process_secret_attribute()` removes values and clears originating change time for password, history, trust, and supplemental credential attributes. `drs_security_access_check()` and `drs_security_access_check_nc_root()` convert DRS object identifiers to DNs or NC roots, then call `dsdb_check_access_on_dn()` for an extended right, mapping denial to `WERR_DS_DRA_ACCESS_DENIED`.

State and persistence: no writes. It can alter in-memory replication attribute responses by redacting secret values.

Dependencies and integration: used by DRS get-changes/add-entry/update paths. Depends on DCE/RPC session info, loadparm, SAMDB/DSDB access checks, security tokens, and object identifier conversion helpers.

Risks and test signals: secret redaction and access checks protect sensitive replication data. Tests should cover disable flag behavior, domain-specific user levels, each secret ATTID, NULL DN denial, bad NC/DN conversion, recycled-object search visibility, and correct WERROR mapping.
