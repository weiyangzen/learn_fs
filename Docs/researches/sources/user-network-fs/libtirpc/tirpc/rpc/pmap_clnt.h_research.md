# sources/user-network-fs/libtirpc/tirpc/rpc/pmap_clnt.h

Purpose: `pmap_clnt.h` declares legacy portmapper v2 client routines for registering and discovering RPC services on port 111.

Important APIs, types, and functions: It declares `pmap_set`, `pmap_unset`, `pmap_getmaps`, `pmap_rmtcall`, `clnt_broadcast`, and `pmap_getport`.

Control flow: Callers register/unregister program/version/protocol/port tuples, query a port for a remote sockaddr, dump mappings, perform UDP-only remote calls through portmapper, or broadcast calls and process responses through a callback.

State and persistence behavior: Portmapper state is external in the local or remote portmapper service. Returned mapping lists are allocated by implementation/XDR code and require appropriate freeing.

Dependencies and integration points: It depends on RPC types, XDR, and `clnt.h`, and complements `pmap_prot.h` and `pmap_rmt.h`. `rpc.h` includes it for legacy API exposure.

Risks: Portmapper v2 is IPv4/port-centric and cannot represent modern transport-independent universal addresses. Broadcast and remote-call behavior uses null authentication and may be quiet on missing registrations.

Test signals: Tests should cover set/unset/getport against rpcbind/portmap compatibility, dump list decoding, UDP remote call, broadcast callback stop behavior, and IPv4-only expectations.
