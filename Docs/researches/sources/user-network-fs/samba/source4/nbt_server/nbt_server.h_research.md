# sources/user-network-fs/samba/source4/nbt_server/nbt_server.h

## Purpose

`nbt_server.h` defines the central in-memory data model for the source4 NBT server and includes the generated NBT server prototypes. It is the coordination header shared by name service, datagram, WINS, IRPC, and startup modules.

## Important APIs, Types, and Functions

`struct nbtd_iface_name` represents one registered NetBIOS name on an interface, including flags, registration time, TTL, and WINS server. `struct nbtd_interface` represents a listening interface with addresses, name socket, datagram socket, name list, and WINS WACK queue. `struct nbtd_server` holds task context, interface lists, WINS server, stats, SAMDB, and unexpected packet server. `NBTD_ASSERT_PACKET()` validates incoming packets and calls `nbtd_bad_packet()`.

## Control Flow

The header has no runtime flow, but it shapes dispatch: handlers recover `nbtd_interface` from socket private data, then reach `nbtd_server` for stats, loadparm, SAMDB, and global interface lists.

## State and Persistence Behavior

All defined structures are runtime-only talloc-managed state. Registered names track TTL and registration time for refresh timers, but persistence is handled elsewhere if at all. The server struct points to SAMDB and WINS contexts rather than storing their data inline.

## Dependencies and Integration Points

It includes libnbt, WINS replication, datagram, IRPC, and messaging headers, then includes `nbt_server_proto.h`. Every C file in this NBT server subset depends on these definitions.

## Risks and Test Signals

Risks include broad coupling through a single header, ABI sensitivity of shared structs, and assertion macro behavior that returns from `void` handlers only. Tests are compile-time coverage across all NBT server modules plus runtime validation that each socket private_data really points to a populated `nbtd_interface`.
