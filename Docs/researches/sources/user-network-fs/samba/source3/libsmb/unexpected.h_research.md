# sources/user-network-fs/samba/source3/libsmb/unexpected.h

Purpose: `unexpected.h` declares the NetBIOS unexpected-packet broker API from `unexpected.c`. It provides opaque server and reader types plus async request functions for creating a local packet subscription channel and reading matching packets.

Important APIs and types: `struct nb_packet_server` and `struct nb_packet_reader` are opaque. `nb_packet_server_create` creates the local broker under an `nmbd_socket_dir`. `nb_packet_dispatch` pushes an incoming `packet_struct` to interested clients. `nb_packet_reader_send/recv` connects a reader and registers filters by packet type, transaction id, and optional mailslot name. `nb_packet_read_send/recv` reads one matched packet.

Control flow and state: callers create a server in a tevent context, dispatch NetBIOS packets as they arrive, and client-side code opens readers that produce tevent requests for matching packet delivery. The header keeps lifetime ownership explicit through talloc contexts and NTSTATUS recv functions.

Dependencies and integration: it includes `replace.h`, tevent, NTSTATUS definitions, and `nameserv.h` for `enum packet_type` and `struct packet_struct`. It is consumed by nmb/name-service code rather than external applications.

Risks: the API is asynchronous and lifetime-sensitive; freeing the server or reader invalidates pending local socket activity. Filtering semantics differ by packet type: NMB uses transaction id, datagrams use mailslot matching.

Test signals: compile tests should cover all declarations. Functional tests should create server/readers, dispatch both NMB and datagram packets, and verify no delivery for mismatched filters.
