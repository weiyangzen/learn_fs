# sources/user-network-fs/samba/source3/lib/netapi/examples/join/getjoinableous.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/join/getjoinableous.c

Purpose: Demonstrates querying organizational units available for domain join with `NetGetJoinableOUs()`.

Important APIs/types/functions: Retrieves username and password from libnetapi context via `libnetapi_get_username()` and `libnetapi_get_password()`, then calls `NetGetJoinableOUs()`.

Control flow: Parses host and domain, obtains credentials already set by common options, calls the API, prints OU strings from the returned array, frees it, and exits.

State and persistence behavior: Read-only directory query; credentials are context state.

Dependencies and integration points: Used by join tools and GUI OU selection before `NetJoinDomain()`.

Risks: Requires credentials; missing credentials are reported as libnetapi errors. Returned OU count and array must be trusted.

Test signals: Query a domain with known joinable OUs and validate output count and cleanup under failure.
