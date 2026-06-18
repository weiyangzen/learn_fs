# sources/user-network-fs/libtirpc/tirpc/rpc/svc_auth_gss.h

Purpose: `svc_auth_gss.h` exposes legacy University of Michigan service-side GSS helper APIs.

Important APIs, types, and functions: It declares `svcauth_gss_set_svc_name` and `svcauth_gss_get_principal`.

Control flow: Servers set the accepted GSS service name, then later retrieve a principal string from an `SVCAUTH` object associated with an authenticated request.

State and persistence behavior: Service-name registration and principal storage are implementation-owned. Returned principal string lifetime depends on the service auth implementation.

Dependencies and integration points: It includes `svc_auth.h` and GSSAPI. It is a legacy companion to the newer `rpcsec_gss.h` server APIs.

Risks: Legacy API behavior may differ from `rpc_gss_set_svc_name` and may have weaker ownership/lifetime documentation. GSS name handling is security-sensitive.

Test signals: Tests should cover service-name registration, principal retrieval after a GSS-authenticated call, failed/unauthenticated retrieval, and coexistence with `rpcsec_gss.h` APIs.
