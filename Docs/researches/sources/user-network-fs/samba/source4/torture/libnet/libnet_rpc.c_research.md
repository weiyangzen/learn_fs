# sources/user-network-fs/samba/source4/torture/libnet/libnet_rpc.c

## Purpose
This file tests `libnet_RpcConnect` across multiple connection levels and interfaces, including expected authentication failures for deliberately bad credentials.

## Important APIs, types, and functions
`test_connect_service()` is the core checker for one interface and connection mode. `torture_rpc_connect()` runs LSA, SAMR, and SRVSVC success cases plus LSA/SAMR bad-credential failures. Public entry points select `LIBNET_RPC_CONNECT_SERVER`, `PDC`, `DC`, `DC_INFO`, or `BINDING`. Key inputs are NDR interface tables for LSARPC, SAMR, and SRVSVC.

## Control flow
The wrapper creates a libnet context with command-line credentials, then calls `libnet_RpcConnect` repeatedly. Success paths expect `NT_STATUS_OK`; bad credential paths rewrite the credential object to `baduser`/`badpassword` and expect `NT_STATUS_LOGON_FAILURE`. The DC-info mode prints returned domain name, SID, realm, and GUID.

## State and persistence behavior
Remote state is not modified. The test mutates the in-memory credential object when checking bad credentials, so later checks in the same context would inherit the bad username/password unless ordered carefully. The current ordering puts bad-credential checks last.

## Dependencies and integration points
The file binds libnet to generated RPC interface tables, `torture_rpc_binding()` for host/binding strings, loadparm workgroup settings for DC/PDC discovery, and Samba credential APIs.

## Risks and edge cases
Credential mutation is intentionally destructive within the test context. Some servers can map authentication failures differently, and environments with anonymous or guest fallback could obscure expected `LOGON_FAILURE`. DC/PDC modes depend on domain discovery rather than a direct server binding.

## Test signals
Passing output shows that libnet can connect to LSA, SAMR, and SRVSVC at each supported selection level, and that authentication failures propagate as expected instead of being treated as transport success.
