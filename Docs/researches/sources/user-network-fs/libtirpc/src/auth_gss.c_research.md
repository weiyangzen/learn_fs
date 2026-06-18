<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_gss.c -->
# sources/user-network-fs/libtirpc/src/auth_gss.c

Purpose: Client-side RPCSEC_GSS authentication implementation for libtirpc.

Important APIs, types, and functions: Exports `authgss_create`, `authgss_create_default`, private-data get/free, `authgss_service`, `rpc_gss_seccreate`, `rpc_gss_set_defaults`, `rpc_gss_max_data_length`, and `is_authgss_client`. Implements auth ops for marshal, validate, refresh/context negotiation, destroy, wrap, and unwrap over `struct rpc_gss_data`.

Control flow: Creation imports/duplicates service names, sets RPCSEC_GSS init credentials, temporarily installs the AUTH on the CLIENT, and runs refresh. Refresh loops over `gss_init_sec_context` and NULLPROC exchanges until established, validating the final verifier. Marshal encodes credentials and MICs the RPC header for data calls. Validate verifies response MICs. Wrap/unwrap delegate to `xdr_rpc_gss_data` for integrity/privacy.

State and persistence behavior: Per-AUTH state includes GSS context, context handle buffer, service/qop/credential tuple, sequence number/window, saved wire verifier, channel bindings, client pointer, and refcount protected by a mutex. Destroy sends RPCSEC_GSS_DESTROY when established, releases GSS buffers/names/context, and frees state when refcount reaches zero.

Dependencies and integration points: Depends on GSSAPI, RPC client calls, rpc_gss utility mapping/error functions, authgss XDR protocol helpers, and libtirpc debug/ref locks. Included when GSS is enabled.

Risks: Context negotiation modifies `clnt->cl_auth` temporarily and must restore it. Failure paths inside `_rpc_gss_refresh` can destroy `auth` while callers still hold local variables. Sequence/QOP verification is security-critical. Saved verifier allocation must be freed on all context-destroy paths.

Test signals: No direct test here; configure/build with GSS and downstream RPCSEC_GSS clients are signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_gss.c -->
