# sources/user-network-fs/samba/source4/nbt_server/packet.c

## Purpose

`packet.c` contains shared packet helpers for the NBT name service: bad-packet logging, self-packet detection, and construction/sending of positive/negative query, registration, release, and WACK replies.

## Important APIs, Types, and Functions

Exports include `nbtd_bad_packet()`, `nbtd_self_packet_and_bcast()`, `nbtd_self_packet()`, `nbtd_name_query_reply_packet()`, `nbtd_name_query_reply()`, `nbtd_negative_name_query_reply()`, `nbtd_name_registration_reply()`, `nbtd_name_release_reply()`, and `nbtd_wack_reply()`.

## Control Flow

Self-packet detection checks broadcast status, whether the packet arrived on a unicast socket, source port, and source address against local interfaces. Query reply construction creates a single answer with NetBIOS rdata entries for each address. Negative replies and registration/release replies mirror the incoming transaction ID and name, set appropriate opcode/rcode flags, and send via `nbt_name_reply_send()`. WACK replies include the original operation in a two-byte data body.

## State and Persistence Behavior

The file only reads interface/server state and increments `stats.total_sent` in send helpers. Packets are allocated under the socket or caller context and freed after send.

## Dependencies and Integration Points

Dependencies include NBT generated NDR structures, service task loadparm for NBT port, socket addresses, and interface private data. Query, defense, release, and WINS paths reuse these helpers for consistent reply formatting.

## Risks and Test Signals

Risks include shallow copying request rdata into registration/release replies, self-packet false positives with spoofed source address/port, address-list length zero behavior, and WACK data encoding. Tests should validate exact packet flags/opcodes/rcodes, multi-address query replies, negative replies, self broadcast suppression, and malformed allocation paths.
