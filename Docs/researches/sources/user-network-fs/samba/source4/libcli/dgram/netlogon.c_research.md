# sources/user-network-fs/samba/source4/libcli/dgram/netlogon.c

Purpose: typed helpers for Netlogon mailslot datagrams over the generic NBT datagram mailslot layer.

Important APIs: `dgram_mailslot_netlogon_send()` NDR-pushes `nbt_netlogon_packet` and sends it to the selected mailslot. `dgram_mailslot_netlogon_reply()` pushes a `nbt_netlogon_response` and sends it to the source of an incoming request. `dgram_mailslot_netlogon_parse_request()` and `_parse_response()` decode request/response payloads.

Control flow: send and parse paths extract or build `DATA_BLOB`s and delegate to generated Netlogon NBT codecs or hand helper functions. Reply constructs the destination socket address from `request->src_addr` and `request->src_port`, creates a client NetBIOS source name, and calls `dgram_mailslot_send()`.

State and persistence: all state is temporary. At debug level 10 a malformed request may be saved as `netlogon.dat`; otherwise there is no persistence.

Dependencies and integration: integrates NBT datagram mailslots with `../libcli/netlogon/netlogon.h`, generated `ndr_nbt`, and socket addressing. Used by older DC discovery and logon browse flows.

Risks: unauthenticated UDP source data drives replies. Parse failures are logged at level 0, which can be noisy if exposed to hostile traffic. Test signals include valid request/response round trips, malformed NDR payloads, missing destination address allocation, and correct source/destination NetBIOS name use.
