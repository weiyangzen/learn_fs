# sources/user-network-fs/samba/source3/utils/nmblookup.c

## Purpose
Standalone NetBIOS Name Service client for querying NBT names, master browsers, node status, and address/name translations.

## Important APIs, Types, and Functions
Global flags hold command-line state. `open_sockets()` binds a UDP socket and enables broadcast. `query_one()` uses `name_query()` for explicit broadcast/unicast or `name_resolve_bcast()` otherwise. `do_node_status()` uses `node_status_query()` and prints names, flags, and MAC address. `node_status_flags()` and `query_flags()` format protocol flags.

## Control Flow
`main()` initializes Samba cmdline/popt, parses options, opens sockets, then processes each node. `-A` performs node status by IP. `-M` changes lookup type for master-browser discovery. `name#hex` overrides NetBIOS type. Failures set a nonzero exit status but later names are still processed.

## State and Persistence
No persistent state. Runtime state is the UDP socket, global options, and temporary query result arrays.

## Dependencies and Integration Points
Depends on Samba cmdline helpers, loadparm NBT client socket address, NetBIOS query/status APIs, socket helpers, address parsing/printing, and optional reverse DNS through `sys_getnameinfo()`.

## Risks
Root-port binding requires privilege. Broadcast queries can be noisy and environment-dependent. Reverse translation skips addresses without PTR records. `#type` parsing is lightly validated.

## Test Signals
Cover no-node usage, invalid options, broadcast/unicast, recursion flag, flags output, master-browser mode, `name#type`, overlong names, returned-address status lookup, `-A` mode, root-port failure, reverse translation, and multi-node exit status.
