# sources/user-network-fs/libtirpc/tirpc/rpc/auth_gss.h

Purpose: `auth_gss.h` declares the lower-level RPCSEC_GSS client authentication structures and helpers used by libtirpc's GSS implementation.

Important APIs, types, and functions: It defines `rpc_gss_proc_t`, `rpc_gss_svc_t`, `RPCSEC_GSS_VERSION`, `struct rpc_gss_sec`, `struct authgss_private_data`, `struct rpc_gss_cred`, `struct rpc_gss_init_res`, `MAXSEQ`, XDR helpers for credentials/init/data, constructors `authgss_create` and `authgss_create_default`, service selection and private-data accessors, logging helpers, and `is_authgss_client`.

Control flow: Clients create an AUTH handle with mechanism/qop/service/credential requirements, perform INIT/CONTINUE_INIT exchanges, then send DATA or DESTROY procedures. `xdr_rpc_gss_data` wraps payload encoding with GSS integrity/privacy behavior based on service.

State and persistence behavior: GSS contexts, context handles, sequence windows, and private auth data persist inside the AUTH implementation. `authgss_get_private_data` exposes a copy-like private-data structure that must be freed through `authgss_free_private_data`.

Dependencies and integration points: It depends on `rpc/clnt.h` and `<gssapi/gssapi.h>`. It integrates with `auth.h` as the RPCSEC_GSS flavor and with service-side GSS code through shared credential structures.

Risks: Sequence-window handling and GSS context lifecycle are security-critical. Incorrect qop/service negotiation can silently downgrade integrity or privacy. Logging helpers can expose sensitive byte dumps if enabled improperly. External OID globals (`krb5oid`, `spkm3oid`) must resolve from the GSS/Kerberos integration.

Test signals: Tests should cover context establishment, continuation tokens, service changes, integrity/privacy data wrapping, sequence number rollover near `MAXSEQ`, destroy messages, and private-data lifetime.
