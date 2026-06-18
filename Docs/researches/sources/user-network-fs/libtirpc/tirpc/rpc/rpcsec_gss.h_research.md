# sources/user-network-fs/libtirpc/tirpc/rpc/rpcsec_gss.h

Purpose: `rpcsec_gss.h` declares the higher-level RPCSEC_GSS public API for creating secure RPC auth handles, configuring services, registering server names/callbacks, retrieving credentials, and discovering mechanisms.

Important APIs, types, and functions: It defines `rpc_gss_service_t`, `rpc_gss_principal_t`, option request/return structs, raw and Unix credential structs, lock and callback structs, error structs, OID aliases, error constants, and functions such as `rpc_gss_seccreate`, `rpc_gss_set_defaults`, max-data-length helpers, `rpc_gss_set_svc_name`, `rpc_gss_getcred`, `rpc_gss_set_callback`, principal/mechanism/qop discovery, version discovery, and error retrieval.

Control flow: Clients create an AUTH handle for a service principal/mechanism/qop/service, optionally inspect returned context options, and use it through normal `CLIENT` calls. Servers register accepted service names and callbacks, then dispatch code can retrieve raw and Unix-mapped credentials from `svc_req`.

State and persistence behavior: GSS contexts, service registrations, callbacks, errors, and credential mappings are implementation-owned. Credential pointers returned by `rpc_gss_getcred` are tied to request/auth context lifetime.

Dependencies and integration points: It depends on GSSAPI, `auth.h`, and `clnt.h`. It complements the lower-level `auth_gss.h` and service auth implementation.

Risks: This API is security-sensitive: default service/qop choices, callback authorization, and credential mapping must be correct. `rpc_gss_principal_t` uses a flexible one-byte tail idiom. Mechanism/qop strings and OIDs require precise ownership and lifetime handling.

Test signals: Tests should cover client context creation, server name registration, callback authorization accept/reject, credential retrieval, max-data calculations for integrity/privacy, mechanism discovery, qop mapping, and error reporting.
