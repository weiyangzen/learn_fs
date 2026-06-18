# sources/user-network-fs/libtirpc/tirpc/netconfig.h

Purpose: `netconfig.h` defines the transport-independent network configuration record and iteration APIs used by TI-RPC client/server creation.

Important APIs, types, and functions: It defines `NETCONFIG`, `NETPATH`, `struct netconfig`, `NCONF_HANDLE`, network semantics constants (`NC_TPI_CLTS`, `NC_TPI_COTS`, `NC_TPI_COTS_ORD`, `NC_TPI_RAW`), flags, protocol family/protocol strings, and APIs such as `setnetconfig`, `getnetconfig`, `getnetconfigent`, `freenetconfigent`, `endnetconfig`, `setnetpath`, `getnetpath`, `endnetpath`, `nc_perror`, and `nc_sperror`.

Control flow: The header exposes iterator-style control flow: callers obtain a handle, repeatedly fetch `struct netconfig *` entries, and end the iteration. Direct lookup returns one entry by netid. Error reporting is via print/string helpers.

State and persistence behavior: The implementation behind these prototypes owns iterator state and allocated `netconfig` entries. The header reserves unused fields for ABI growth.

Dependencies and integration points: `clnt.h`, `svc.h`, `nettype.h`, and rpcbind APIs use `struct netconfig` to select TCP, UDP, loopback, IPv4, IPv6, and visibility semantics.

Risks: String constants and numeric semantics are ABI/protocol selection inputs; changing them breaks configuration parsing. Memory ownership must be respected: entries from direct lookup require `freenetconfigent`, while iterator entries are tied to the handle.

Test signals: Tests should parse `/etc/netconfig` or fixture data, iterate `NETPATH`, lookup visible TCP/UDP entries, and verify error reporting and cleanup behavior.
