# sources/user-network-fs/samba/source4/libcli/dgram/libdgram.h

Purpose: internal/public header for raw async NBT datagram and mailslot support.

Important types: `struct nbt_dgram_request` represents one queued outgoing encoded datagram and destination. `struct nbt_dgram_socket` holds the socket, tevent context/fd, send queue, mailslot handlers, and generic incoming callback. `dgram_mailslot_handler_t` and `struct dgram_mailslot_handler` model per-mailslot callbacks with private data.

Important APIs: declares raw/structured datagram send, socket init, incoming handler registration, mailslot name lookup, handler registration, temporary reply slot allocation, payload extraction, generic mailslot send, and typed netlogon/browse send/reply/parse helpers.

Control flow contract: callers create a socket, register mailslot or generic handlers, then queue packets through `nbt_dgram_send()` or type-specific mailslot helpers. Receive-side dispatch is performed by `dgramsocket.c`.

State and persistence: only in-memory handler and send queues are described. Handler lifetime is controlled by talloc; freeing a handler stops listening via the destructor in `mailslot.c`.

Dependencies and integration: includes Netlogon definitions and relies on generated NBT structs from the broader Samba include graph. This header is the integration point between datagram socket plumbing and browse/netlogon packet modules.

Risks: exposed structs allow direct mutation by internal callers. Temporary mailslot naming and handler lifetime must be used carefully to avoid reply loss or stale callbacks. Test signals should validate structure ownership, temp handler removal, and all declared helper paths.
