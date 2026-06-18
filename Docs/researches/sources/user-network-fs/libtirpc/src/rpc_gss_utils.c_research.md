<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_gss_utils.c -->
# sources/user-network-fs/libtirpc/src/rpc_gss_utils.c

Purpose: RPCSEC_GSS utility API for mechanism/QOP discovery and thread-specific error reporting.

Important APIs and functions: `rpc_gss_get_error()`, `rpc_gss_set_error()`, and `rpc_gss_clear_error()` manage `rpc_gss_error_t` values. `rpc_gss_get_mechanisms()`, `rpc_gss_get_mech_info()`, `rpc_gss_get_versions()`, `rpc_gss_is_installed()`, `rpc_gss_mech_to_oid()`, `rpc_gss_oid_to_mech()`, `rpc_gss_qop_to_num()`, and `rpc_gss_num_to_qop()` expose static Kerberos v5 mechanism/QOP mappings. Internal helpers search mechanism and QOP tables and compare OIDs.

Control flow: `__rpc_gss_error()` lazily creates a thread-specific key, allocates one error object per thread, and falls back to a static error object if key creation or allocation fails. Mechanism APIs validate null arguments, search static tables, set `EINVAL` or `ENOENT` on failure, and clear errors on success.

State and persistence: thread-specific error objects persist until thread exit through TSD destructors. Mechanism/QOP tables are static read-only data. Supported mechanisms are limited to Kerberos v5 and its principal-name OID, with default QOP only.

Dependencies and integration points: depends on `<rpc/auth_gss.h>`, `<rpc/rpcsec_gss.h>`, and GSS/Kerberos OID definitions. `svc_auth_gss.c` calls `rpc_gss_oid_to_mech()` and `rpc_gss_num_to_qop()` to populate credentials and QOP strings.

Risks: the static table emulates Solaris files and can become incomplete if the underlying GSS implementation supports more mechanisms or QOPs. Fallback to a shared static error object means error reporting is less thread-isolated under allocation/key failures.

Test signals: mechanism name/OID round trips, null-argument error reporting, unknown mechanism/QOP failures, per-thread independent error values, and GSS builds with both MIT/Heimdal headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_gss_utils.c -->
