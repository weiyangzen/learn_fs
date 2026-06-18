# sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/netlogon_control.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/netlogon_control.c

Purpose: Demonstrates querying Netlogon control state with `I_NetLogonControl()`.

Important APIs/types/functions: Supports result levels 1-4 and prints `NETLOGON_INFO_1/2/3/4` fields such as flags, trusted DC, connection status, trust verification, and logon attempts.

Control flow: Parses hostname, function code, and level, calls `I_NetLogonControl()`, casts the returned buffer by level, prints diagnostics using `libnetapi_errstr()`, frees the buffer, and exits.

State and persistence behavior: Mostly read-only diagnostics, though function codes may trigger netlogon actions depending on server implementation.

Dependencies and integration points: Netlogon administrative sample; related to `netlogon_control2` and `nltest`.

Risks: Function code is numeric and not constrained by the sample. Some codes may have side effects.

Test signals: Query levels 1-4 against a domain member/DC and compare status fields with server logs.
