# sources/user-network-fs/samba/source4/nbt_server/nodestatus.c

## Purpose

`nodestatus.c` answers NetBIOS node status queries by returning the active local names registered on the addressed interface.

## Important APIs, Types, and Functions

`nbtd_node_status_reply_packet()` builds a status response packet. `nbtd_query_status()` validates and dispatches incoming status queries. The local `nbtd_node_status_reply()` sends the reply. The code uses `nbtd_find_iname()`, NBT status rdata structures, and `nbt_name_reply_send()`.

## Control Flow

Packet construction counts active, non-`*` interface names, allocates one answer record, duplicates the requested name, fills status rdata, then iterates names again to write padded 15-character names, type, and flags. Query handling validates qdcount, type, and class, finds an active matching name on the interface, and sends the status reply or silently ignores missing names.

## State and Persistence Behavior

No state is persisted. The function reads active flags and names from `iface->names` and increments sent statistics through the server in the send helper.

## Dependencies and Integration Points

Dependencies include generated NBT structures, socket send helpers, interface name registration state, and the query dispatcher in `query.c`.

## Risks and Test Signals

Risks include name padding/truncation behavior, excluding wildcard `*`, silent no-reply for missing names, and memory cleanup on partial allocation failure. Tests should cover status queries for active/inactive/missing names, multiple aliases, wildcard exclusion, flag preservation, and malformed query validation.
