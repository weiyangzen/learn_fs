# sources/user-network-fs/samba/source4/dns_server/dns_server.c

## Purpose
`dns_server.c` is the Samba AD DC internal DNS service entry point. It registers the `dns` service, initializes AD-backed DNS state, opens TCP and UDP listeners, accepts packets, dispatches DNS query/update opcodes, signs TSIG replies, truncates large UDP responses, and exposes an IRPC reload hook for zone refreshes.

## Important APIs, Types, and Functions
- `server_service_dns_init()` registers the service with Samba's service framework.
- `dns_task_init()` performs role checks, opens `samdb`, prepares DNS credentials, loads zones, binds interfaces, and registers the `DNSSRV_RELOAD_DNS_ZONES` IRPC handler.
- `dns_process_send()/dns_process_recv()` are the central async DNS packet parser/dispatcher/serializer pair.
- `dns_tcp_accept()`, `dns_tcp_call_loop()`, and callbacks process length-prefixed DNS-over-TCP PDUs through `tstream`.
- `dns_udp_call_loop()` and callbacks process datagram DNS requests through `tdgram`.
- `dns_add_socket()` binds matching TCP and UDP sockets for one local address.
- `dns_server_reload_zones()` rebuilds the in-memory `dns->zones` list using `dns_common_zones()`.
- Local state structs include `dns_socket`, `dns_udp_socket`, `dns_tcp_connection`, `dns_process_state`, `dns_tcp_call`, and `dns_udp_call`.

## Control Flow
Startup rejects standalone/member-server roles and continues only for `ROLE_ACTIVE_DIRECTORY_DC`. If `interfaces` plus `bind interfaces only` is configured, it loads the configured interface list; otherwise it binds wildcard addresses. The task initializes credentials, connects to `samdb` under `system_session()`, prefers a stored `DNS/<dns hostname>` service principal when present, falls back to the machine account, initializes the TKEY store, loads zones, starts sockets, and registers the `dnssrv` IRPC name plus reload handler.

Packet processing validates the minimum DNS header length, NDR-decodes `dns_name_packet`, rejects replies, sets reply flags and recursion availability, copies the input packet into `out_packet`, verifies TSIG, then dispatches by opcode. Query processing is asynchronous through `dns_server_process_query_send/recv`; update processing is synchronous through `dns_server_process_update()`. Unsupported opcodes become `NOT_IMPLEMENTED`.

TCP reads a complete two-byte-length-prefixed PDU, strips the length header, launches packet processing, immediately posts another read for pipelining, and writes a new two-byte length plus response on a send queue. UDP posts a new receive after each datagram, then sends the serialized response on a queued datagram send. UDP responses larger than `DNS_MAX_UDP_PACKET_LENGTH` are rebuilt with `DNS_FLAG_TRUNCATION` and no answer/authority/additional records so clients retry over TCP.

## State and Persistence
Long-lived state is `struct dns_server`: service task, `samdb`, loaded zone list, TKEY ring, and server credentials. Socket and connection state is talloc-scoped under the service/connection. Persistent DNS data lives in AD via helper calls in other files; this file only opens `samdb`, reloads zone metadata, and routes update/query operations. The IRPC reload path atomically swaps the in-memory zone list and frees the old list.

## Dependencies and Integration Points
The file integrates Samba service/task, process model, `tevent`, `tstream`, `tdgram`, socket/interface helpers, NDR DNS codecs, `samdb`, credentials, TSIG helpers, DNS query/update modules, `dnsserver_common`, and IRPC messaging. Configuration inputs include server role, interface binding, DNS port, DNS forwarder, DNS hostname, and socket options.

## Risks and Edge Cases
- Unknown non-OK DNS errors are converted to fallback wire replies by mutating the original packet bytes; this preserves a response but can hide serialization-specific failures.
- UDP truncation depends on rebuilding the packet after mutating `out_packet`; TSIG or future EDNS handling needs care around this path.
- The TKEY store is a fixed-size ring initialized here but managed elsewhere, so long-lived authenticated update behavior depends on external eviction logic.
- `dns_task_init()` contains a redundant `if (!dns_spn)` after successful search; harmless but misleading.
- Zone reload frees the entire old list after swapping; any future code holding zone pointers across reload would be unsafe.

## Test Signals
Coverage is indirect through Samba DNS server integration/torture tests, dynamic update tests, query tests, and IRPC reload paths. Useful focused tests include malformed packets under 12 bytes, reply packets, TSIG failure/signing, TCP pipelining, UDP truncation at 1232 bytes, AD DC role gating, interface binding variants, and zone reload after DB mutation.
