# sources/user-network-fs/samba/source4/nbt_server/nbt_server.c

## Purpose

`nbt_server.c` is the service-task entry point for Samba's source4 NBT server. It initializes interfaces, unexpected packet compatibility support, SAMDB, WINS server support, IRPC services, message handlers, NetBIOS name registration, process naming, and pidfile lifecycle.

## Important APIs, Types, and Functions

The service entry point is `server_service_nbtd_init()`, which registers service name `nbt`. `nbtd_task_init()` performs startup. `nbtd_server_msg_send_packet()` handles source3-style `MSG_SEND_PACKET` messages. `nbtd_server_destructor()` removes the `nmbd` pidfile.

## Control Flow

Startup loads configured interfaces, rejects empty interface lists and `disable netbios = yes`, allocates `nbtd_server`, starts NBT interfaces, creates the unexpected packet server under the configured or dynamic nmbd socket directory, opens SAMDB as system, initializes the WINS server, registers IRPC and `MSG_SEND_PACKET`, starts local name registration, adds messaging name `nbt_server`, and creates the nmbd pidfile. `MSG_SEND_PACKET` validates a `packet_struct`, resolves the outgoing interface, adjusts datagram source fields, builds a raw packet into a fixed buffer, and sends it via name or datagram socket.

## State and Persistence Behavior

The service stores all live server state in `struct nbtd_server`. Persistent side effects are the `nmbd` pidfile and any WINS/SAMDB effects delegated to other components. Name registrations and stats are memory-resident.

## Dependencies and Integration Points

Dependencies include Samba service task registration, interface loading, pidfile utilities, SAMDB/system session, WINS server init, messaging, source3 packet compatibility, socket utilities, dynamic config, and NBT interface/registration modules.

## Risks and Test Signals

Risks include fixed 1024-byte raw packet build buffer, strict `packet_struct` length validation across ABI changes, source address rewrite for datagrams, startup termination on optional component failures, and pidfile cleanup ordering. Tests should start with NetBIOS disabled/enabled, no interfaces, WINS enabled, MSG_SEND_PACKET name and datagram sends, invalid packet inputs, SAMDB failure, and pidfile create/unlink behavior.
