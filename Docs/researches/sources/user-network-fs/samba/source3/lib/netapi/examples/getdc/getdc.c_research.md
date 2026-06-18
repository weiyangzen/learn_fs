# sources/user-network-fs/samba/source3/lib/netapi/examples/getdc/getdc.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/getdc/getdc.c

Purpose: Demonstrates legacy `NetGetDCName()` domain-controller lookup.

Important APIs/types/functions: Calls `NetGetDCName(hostname, domain, &buffer)` and prints the returned string.

Control flow: Initializes libnetapi, parses common options, requires hostname, optionally accepts a domain, calls the API, prints the DC name on success, frees `buffer`, and releases context.

State and persistence behavior: Read-only network discovery with no local persistence.

Dependencies and integration points: Shows the older NetAPI DC lookup beside the richer `DsGetDcName()` sample.

Risks: Requires correct positional arguments; prints `libnetapi_errstr()` rather than context error string.

Test signals: Run against domain member and standalone contexts; compare with `dsgetdc` results.
