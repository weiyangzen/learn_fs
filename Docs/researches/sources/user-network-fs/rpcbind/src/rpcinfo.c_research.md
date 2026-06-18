<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcinfo.c -->
# sources/user-network-fs/rpcbind/src/rpcinfo.c

Purpose: Implements the `rpcinfo` diagnostic CLI for dumping rpcbind/portmap registrations, pinging RPC services, broadcasting NULLPROC probes, deleting registrations, querying address lists, and printing rpcbind statistics.

Important APIs, types, and functions: Mode constants identify PMAP dump, TCP/UDP ping, broadcast, deletion, address ping, program ping, RPCB dump, short dump, address list, and stats. Core functions include `main`, `local_rpcb`, `ip_ping`, `pmapdump`, `ip_getclient`, `brdcst`, `rpcbdump`, `rpcbaddrlist`, `rpcbgetstat`, `deletereg`, `clnt_addr_create`, `addrping`, `progping`, `clnt_rpcbind_create`, `getclnthandle`, `pstatus`, `print_rmtcallstat`, and `print_getaddrstat`. Short dump aggregation uses `rpcbdump_short`, `verslist`, and `netidlist`.

Control flow: `main` parses mutually exclusive options and selects a function; no option defaults to a full RPCB dump or program ping depending on argument count. Local operations use AF_LOCAL `_PATH_RPCBINDSOCK` and optionally an abstract socket. Remote rpcbind clients are created over preferred nettype families (`circuit_n`, `circuit_v`, `datagram_v`) or an explicit netid. Ping modes issue NULLPROC calls, infer supported version ranges from `RPC_PROGVERSMISMATCH`, then iterate versions. Dump modes call `RPCBPROC_DUMP`, fall back to RPCB v4 or PMAP v2 when needed, and print long or grouped output. Stats mode calls `RPCBPROC_GETSTAT` and prints per-version counts plus getaddr/rmtcall breakdowns.

State and persistence: The tool keeps only process-local transient client handles, converted linked lists returned by RPC calls, and formatting aggregation lists. It does not persist state, but `deletereg` changes daemon state by calling `rpcb_unset`.

Dependencies and integration points: Depends on libtirpc client APIs, rpcbind/portmap protocols, `/etc/rpc` lookups via `getrpcbyname`/`getrpcbynumber`, netconfig/nettype iteration, local rpcbind socket paths, and standard resolver APIs. It is both a test/debug client for `rpcbind.c`/`rpcb_svc_com.c` and an administrative tool that can remove mappings.

Risks: The file forces `PORTMAP` on, so code paths assume portmap headers and APIs. Several operations call `exit` from helper functions, which simplifies CLI flow but complicates library reuse. Version probing can loop over very large ranges if a server accepts version 0 and MAX_VERS. Some fallback PMAP conversion allocates mixed static and heap strings. `SUN_LEN_A` handles abstract sockets with Linux-specific semantics.

Test signals: CLI tests should cover invalid/mutually exclusive options, local and remote dumps, v3/v4 fallback, PMAP fallback, explicit netid handling, direct address ping, program ping with known and unknown versions, broadcast output, deletion failure/success, and stats output formatting. Mock or containerized rpcbind instances are useful because many branches depend on real RPC error codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcinfo.c -->
