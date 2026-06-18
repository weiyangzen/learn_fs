# sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/nltest.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/netlogon/nltest.c

Purpose: Provides a richer `nltest`-style sample for netlogon control, secure-channel operations, DC discovery, and flag decoding.

Important APIs/types/functions: Defines option ids for server, db flags, secure-channel query/reset/verify, DC discovery flags, site/account fields, and DNS return controls. Helpers print `NETLOGON_INFO_1/2` results, DC flags, and `DOMAIN_CONTROLLER_INFO`. Main calls `I_NetLogonControl2()` for several operations and `DsGetDcName()` for discovery.

Control flow: Parses many popt options into operation flags. It initializes libnetapi, executes the selected control path, passes optional domain/account data to Netlogon control calls, prints status or DC information, and exits through shared cleanup.

State and persistence behavior: Some operations are read-only, but secure-channel reset, rediscovery, and db flag operations can alter Netlogon runtime state on the target server.

Dependencies and integration points: Combines libnetapi, Netlogon control, and DC locator behavior in one diagnostic tool.

Risks: Administrative side effects are exposed through command flags. Flag combinations can be invalid and are only lightly validated. Returned NetAPI buffers are not explicitly freed on every path before process exit. Output is human-oriented.

Test signals: Run query-only flags in CI-like integration, and reserve reset/dbflag operations for isolated domain controller/member tests.
