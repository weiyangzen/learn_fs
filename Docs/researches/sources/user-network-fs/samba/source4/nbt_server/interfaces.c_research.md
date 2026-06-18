# sources/user-network-fs/samba/source4/nbt_server/interfaces.c

## Purpose

`interfaces.c` manages NBT server listening interfaces, name and datagram sockets, request dispatch, unexpected response redirection, address-list construction, and interface selection for outgoing requests/replies.

## Important APIs, Types, and Functions

Important functions are `nbtd_request_handler()`, `nbtd_unexpected_handler()`, `nbtd_find_iname()`, `nbtd_add_socket()`, `nbtd_add_wins_socket()`, `nbtd_startup_interfaces()`, `nbtd_address_list()`, `nbtd_find_request_iface()`, and `nbtd_find_reply_iface()`.

## Control Flow

Startup optionally creates a wildcard broadcast-style interface when `bind interfaces only` is disabled, then creates per-IPv4-interface sockets for each broadcast-capable interface, and optionally creates a WINS client interface. Each real interface gets a broadcast name socket, unicast name socket, unexpected handler, and datagram setup. Incoming NBT name packets increment stats, ignore self broadcast packets, and dispatch by opcode to query, defense, release/multihome WINS handling, or bad-packet logging. Unexpected replies are matched against request IDRs on broadcast, WINS, or other sockets; unmatched replies are serialized and sent to the unexpected packet server.

## State and Persistence Behavior

This file builds and links `struct nbtd_interface` objects into `nbtsrv->interfaces`, `bcast_interface`, and `wins_interface`. It owns socket pointers and per-interface names lists, but persistent name state is only memory-resident.

## Dependencies and Integration Points

Dependencies include network interface enumeration, socket/listen APIs, libnbt name sockets, libdgram setup, WINS server hooks, ID tree request tracking, source3 unexpected packet compatibility, and loadparm options. It is called during NBT task initialization.

## Risks and Test Signals

Risks include IPv4-only filtering, broadcast address binding portability, wildcard-interface selection semantics, unexpected reply misrouting by transaction ID collision, loopback address filtering in replies, and null-interface fallback assumptions. Tests should cover bind-interfaces-only on/off, multiple interfaces, loopback plus non-loopback, WINS client interface, broadcast self-packet suppression, unmatched unexpected response forwarding, and reply interface selection.
