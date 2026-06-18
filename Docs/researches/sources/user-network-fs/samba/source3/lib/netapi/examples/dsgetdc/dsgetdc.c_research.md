# sources/user-network-fs/samba/source3/lib/netapi/examples/dsgetdc/dsgetdc.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/dsgetdc/dsgetdc.c

Purpose: Demonstrates `DsGetDcName()` discovery of a domain controller and prints returned controller metadata.

Important APIs/types/functions: Uses `DOMAIN_CONTROLLER_INFO`, accepts hostname/domain/site flags, parses flags as hex, and frees the result with `NetApiBufferFree()`.

Control flow: Initializes libnetapi, parses common options, requires a domain argument, optionally reads server/site/flags, calls `DsGetDcName()`, prints DC name/address/domain/forest/flags/site fields, then frees buffers and context.

State and persistence behavior: No persistent state; discovery is network/RPC state.

Dependencies and integration points: Integrates popt examples with domain discovery APIs used by join and netlogon workflows.

Risks: Flags are parsed with `sscanf("%x")` without strong validation. Output assumes non-NULL strings from the API.

Test signals: Run against a known AD domain with default and site/flag variants; verify graceful error when no DC is reachable.
