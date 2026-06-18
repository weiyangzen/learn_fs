# sources/user-network-fs/samba/source4/nbt_server/dgram/browse.c

## Purpose

`dgram/browse.c` handles browser-service mailslot datagrams received by the NBT datagram server. In this source4 implementation it parses and logs browse packets rather than acting as a full browser election/announcement engine.

## Important APIs, Types, and Functions

`nbtd_mailslot_browse_handler()` is the mailslot callback. `nbt_browse_opcode_string()` maps `enum nbt_browse_opcode` values to readable names for debug logs. The handler uses `dgram_mailslot_browse_parse()` and optional `NDR_PRINT_DEBUG()`.

## Control Flow

The handler allocates a `struct nbt_browse_packet`, parses the incoming datagram into it, logs opcode, destination NetBIOS name, mailslot, and source address, prints full NDR detail at high debug levels, and frees the parsed packet. Parse or allocation failures go to a common debug failure path.

## State and Persistence Behavior

No state is persisted or mutated beyond temporary talloc allocations and debug logging. The datagram socket and mailslot handler registration are managed by `dgram/request.c`.

## Dependencies and Integration Points

Dependencies include libdgram mailslot parsing, generated NBT browse structures, socket addresses, and the NBT server datagram setup. The browse handler is registered for `NBT_MAILSLOT_BROWSE`.

## Risks and Test Signals

Risks include accepting but ignoring browse semantics, null opcode strings for unrecognized opcodes, and failure logging that calls `nbt_name_string()` with a possibly failed allocation context. Tests should cover each known browse opcode, malformed browse datagrams, unknown opcodes, and high-debug NDR printing.
