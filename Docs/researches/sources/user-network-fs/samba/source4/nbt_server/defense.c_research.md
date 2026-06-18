# sources/user-network-fs/samba/source4/nbt_server/defense.c

## Purpose

`defense.c` defends locally registered NetBIOS names against incoming name registration or refresh requests. It decides whether to answer with an active-name conflict or forward the request to the WINS server handling path.

## Important APIs, Types, and Functions

The file exports `nbtd_request_defense()`. It uses `nbtd_self_packet()`, `nbtd_find_iname()`, `nbtd_name_registration_reply()`, `nbtd_winsserver_request()`, and the `NBTD_ASSERT_PACKET` validation macro from `nbt_server.h`.

## Control Flow

If the request originates from one of Samba's own interfaces, it is treated as WINS-client-to-WINS-server traffic and forwarded to `nbtd_winsserver_request()`. Otherwise the function validates query/additional counts, question type/class, additional record type/class, and NetBIOS rdata length. It then looks for an active local name. Non-group, non-logon active names are defended by sending a registration reply with `NBT_RCODE_ACT`; other cases are delegated to WINS server logic.

## State and Persistence Behavior

The file does not create or persist state. It reads the interface's in-memory registered name list and increments no counters directly; dispatch counters are updated by the caller in `interfaces.c`.

## Dependencies and Integration Points

Dependencies include NBT packet structures, interface name state from `nbt_server.h`, WINS server request handling, socket address data, and generated NBT constants. `nbtd_request_handler()` dispatches register/refresh opcodes here.

## Risks and Test Signals

Risks include overly strict packet assertions dropping unusual but tolerated clients, not defending group/logon names, self-packet classification errors, and WINS forwarding loops. Tests should send registration/refresh packets for active unique names, group names, logon names, malformed records, and self-originated requests.
