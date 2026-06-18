# sources/user-network-fs/libtirpc/tirpc/rpc/auth.h

Purpose: `auth.h` defines the client-side RPC authentication ABI, common credential/verifier structures, auth status codes, DES block type, authenticator vtable, and public constructors/utilities for AUTH_NONE, AUTH_SYS/UNIX, AUTH_DES, and RPCSEC_GSS integration.

Important APIs, types, and functions: Key types include `sec_data_t`, `dh_k4_clntdata_t`, `enum auth_stat`, `des_block`, `struct opaque_auth`, and `AUTH` with `auth_ops`. Macros dispatch operations such as `AUTH_MARSHALL`, `AUTH_VALIDATE`, `AUTH_REFRESH`, `AUTH_WRAP`, and `AUTH_UNWRAP`. Constructors and helpers include `authunix_create`, `authunix_create_default`, `authnone_create`, `authdes_create`, `authdes_pk_create`, `authdes_seccreate`, `xdr_opaque_auth`, netname helpers, keyserv helpers, and server auth entry points.

Control flow: Client transports call the AUTH vtable to marshal credentials, validate response verifiers, refresh credentials after auth errors, and wrap/unwrap RPC body XDR. Flavor implementations fill the vtable and private state. Server auth dispatch functions are declared for use by service-side authentication.

State and persistence behavior: `AUTH` instances own credentials, verifiers, DES key material, vtable pointer, and flavor-specific private data until destroyed through the vtable. `_null_auth` is an exported static opaque auth object.

Dependencies and integration points: This header depends on XDR, client status, sockets/types, and is included by `clnt.h`, `svc_auth.h`, RPC message code, and GSS/DES/UNIX flavor headers. It is central to request marshaling and service authentication.

Risks: Many macros dereference vtable pointers without null checks; partially initialized `AUTH` handles crash. DES and AUTH_SYS are weak/legacy mechanisms. The header mixes old K&R-compatible conventions and modern prototypes, so ABI compatibility constrains changes. `authany_wrap`/`authany_unwrap` prototypes are untyped `int(void)`, reflecting compatibility rather than type-safe XDR signatures.

Test signals: Tests should cover AUTH_NONE/UNIX construction, XDR opaque auth bounds at `MAX_AUTH_BYTES`, auth refresh/retry behavior, wrap/unwrap passthrough and GSS behavior, and ABI compatibility with legacy names `AUTH_NULL`, `AUTH_SYS`, and `AUTH_UNIX`.
