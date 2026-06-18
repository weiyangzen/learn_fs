# sources/user-network-fs/samba/source3/nmbd/nmbd_proto.h

## Purpose
`nmbd_proto.h` is the cross-module prototype header for the `source3/nmbd` subsystem. It exposes functions for name registration, packet routing, WINS, browsing, elections, subnets, workgroups, server lists, async DNS, and logon processing.

## Important APIs, types, and functions
It declares packet APIs (`queue_*`, `reply_netbios_packet`, `listen_for_packets`, `send_mailslot`), WINS APIs (`initialise_wins`, `wins_process_*`, storage helpers), browse APIs, name-list APIs, subnet APIs, and workgroup/server-list APIs. The file also contains duplicate declarations for `queue_dns_query` and `kill_async_dns_child`.

## Control flow
The header has no executable control flow, but it defines the compile-time linkage graph for the daemon. Packet dispatch reaches WINS, incoming request, browse, and logon handlers; WINS calls query and reply helpers; announcement/sync code calls workgroup and server-list APIs; main-loop code calls packet, DNS, election, expiration, and persistence functions.

## State and persistence behavior
No state is stored here. The declared functions collectively mutate subnet lists, response lists, workgroup/server lists, WINS TDB data, browse.dat/wins.dat files, async DNS queues, and packet queues.

## Dependencies and integration points
Every prototype depends on shared `nmbd.h` structs and callback typedefs. This header is the broad integration surface for many mutually dependent C files in nmbd.

## Risks and edge cases
Prototype drift can break builds or hide mismatches. Duplicate declarations are maintenance artifacts. The exposed API surface is broad and grants many modules access to global singleton state.

## Test signals
A full Samba build with warnings enabled is the primary signal. Runtime integration tests for packet, WINS, browse, election, and logon paths indirectly validate the declared interfaces.
