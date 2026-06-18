# sources/user-network-fs/samba/source4/nbt_server/dgram/request.c

## Purpose

`dgram/request.c` sets up NetBIOS datagram sockets on port 138, registers static mailslot handlers, and forwards otherwise unexpected direct-unique datagrams to the source3 unexpected-packet compatibility server.

## Important APIs, Types, and Functions

The static `mailslot_handlers[]` table maps `NBT_MAILSLOT_NETLOGON`, `NBT_MAILSLOT_NTLOGON`, and `NBT_MAILSLOT_BROWSE` to callbacks. Exported functions are `dgram_request_handler()` and `nbtd_dgram_setup()`.

## Control Flow

`nbtd_dgram_setup()` optionally creates a broadcast datagram socket for non-wildcard interfaces, always creates a unicast datagram socket, binds them to the configured datagram port, installs `dgram_request_handler()`, and registers mailslot listeners on both sockets. `dgram_request_handler()` logs unexpected mailslots/general datagrams, prints packet detail at debug level, and only forwards `DGRAM_DIRECT_UNIQUE` packets by NDR-pushing them, converting to source3 `packet_struct`, dispatching to `nb_packet_server`, and freeing the packet.

## State and Persistence Behavior

The function stores the unicast datagram socket on `iface->dgmsock`; broadcast socket ownership is held by talloc and mailslot callbacks. It does not persist data. Unexpected packet forwarding is transient.

## Dependencies and Integration Points

Dependencies include libdgram sockets/mailslots, socket binding, loadparm datagram port, NDR NBT marshalling, source3 `parse_packet()`/`nb_packet_dispatch()`, and server interface state. `interfaces.c` calls this for every listening NBT interface.

## Risks and Test Signals

Risks include binding failures on broadcast addresses, only forwarding direct-unique datagrams, registering NTLOGON to the Netlogon handler rather than `ntlogon.c`, and lifetime assumptions for unnamed broadcast sockets. Tests should cover wildcard and per-interface setup, broadcast/unicast mailslots, unexpected direct-unique forwarding, non-direct datagram drop, and bind failure cleanup.
