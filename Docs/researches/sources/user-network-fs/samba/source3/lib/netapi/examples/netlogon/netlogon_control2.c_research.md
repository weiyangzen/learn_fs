# sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/netlogon_control2.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/netlogon_control2.c

Purpose: Demonstrates `I_NetLogonControl2()`, the Netlogon control API variant that accepts data such as a domain name.

Important APIs/types/functions: Uses levels 1-4 with `NETLOGON_INFO_*` structures and passes a hardcoded `"TEST"` domain buffer to the API.

Control flow: Parses hostname, optional function code and level, duplicates the domain string, calls `I_NetLogonControl2()`, prints the same level-specific diagnostics as `netlogon_control`, frees the NetAPI buffer and context.

State and persistence behavior: Diagnostic/control RPC with possible server-side effects depending on function code; local domain string is heap allocated but not freed in the sample.

Dependencies and integration points: Simple precursor to the more complete `nltest` sample.

Risks: Hardcoded data makes many control codes unrealistic. Numeric function codes are unchecked. Small memory leak for `domain`.

Test signals: Exercise query and trust-verification function codes with expected domain data and validate returned status structures.
