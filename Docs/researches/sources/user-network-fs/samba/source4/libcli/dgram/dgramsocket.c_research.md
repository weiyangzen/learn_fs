# sources/user-network-fs/samba/source4/libcli/dgram/dgramsocket.c

Purpose: low-level event-driven UDP/138 NetBIOS datagram socket support for Samba's NBT datagram and mailslot clients.

Important APIs: `nbt_dgram_socket_init()` creates the datagram socket, enables broadcast, and installs a tevent fd handler. `dgram_set_incoming_handler()` installs a generic packet handler. `nbt_dgram_send_raw()` queues an already encoded datagram. `nbt_dgram_send()` NDR-encodes an `nbt_dgram_packet` and queues it.

Control flow: `dgm_socket_handler()` dispatches writable events to `dgm_socket_send()` and readable events to `dgm_socket_recv()`. Receive reads pending bytes, parses an `nbt_dgram_packet`, extracts a mailslot name when present, then dispatches to a registered mailslot handler or a generic incoming handler. Send drains `send_queue` with `socket_sendto()` and disables write events once empty.

State and persistence: `struct nbt_dgram_socket` owns the socket, fd event, outgoing request list, handler list, and incoming callback. No persistent storage exists. Queued sends are talloc children of the socket and are freed after successful or failed send.

Dependencies and integration: uses tevent fd readiness, Samba socket abstraction, NDR NBT packet codecs, and dlink list macros. It is the transport beneath browse and netlogon datagram mailslot helpers.

Risks: UDP datagrams are unauthenticated and may be spoofed. `socket_pending()` size drives allocation, so parse and allocation failure behavior matters. If a mailslot handler frees socket state during callback, lifetime assumptions should be tested. Test signals include handler dispatch by case-insensitive mailslot name, generic fallback dispatch, send queue drain, raw send copy behavior, malformed packet logging, and write interest shutdown.
