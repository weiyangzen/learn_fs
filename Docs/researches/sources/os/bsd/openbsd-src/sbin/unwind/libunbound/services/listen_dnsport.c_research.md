# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/listen_dnsport.c

## Purpose
Implements Unbound's listener setup and runtime request handling for DNS transports in OpenBSD `unwind`: UDP, TCP, local sockets, TLS/DoT, HTTP/2 DoH, DNSCrypt hooks, PROXYv2 flags, UDP ancillary packet info, socket timestamping, and DNS-over-QUIC when compiled with ngtcp2.

## Main Responsibilities
- Create UDP/TCP/local listening sockets with platform-specific options.
- Build `listen_port` lists from config interfaces, wildcard/default addresses, automatic interfaces, and per-interface port overrides.
- Convert open ports into `comm_point` event handlers.
- Track stream-response memory, HTTP/2 query buffers, and HTTP/2 response buffers with locks.
- Manage pipelined TCP query state and queued responses.
- Parse and service HTTP/2 DoH streams with nghttp2 callbacks.
- Manage DoQ connection tables, connection IDs, timers, streams, packet I/O, TLS/QUIC setup, and memory accounting.

## Socket Setup
- `create_udp_sock()` handles systemd activation, `SO_REUSEADDR`, `SO_REUSEPORT`/`SO_REUSEPORT_LB`, transparent/freebind options, receive/send buffers, DSCP, IPv6-only behavior, IPv6 minimum MTU/PMTU controls, IPv4 PMTU behavior, bind, and nonblocking mode.
- `create_tcp_accept_sock()` creates/listens TCP sockets with reuse, transparent/freebind, MSS, `TCP_NODELAY`, DSCP, IPv6-only behavior, TCP Fast Open, and nonblocking mode.
- `create_local_accept_sock()` creates AF_LOCAL stream sockets, unlinks stale paths, binds, listens, and supports systemd activation where available.
- `set_recvpktinfo()` enables destination-address ancillary data for wildcard/automatic UDP and DoQ sockets.
- `set_recvtimestamp()` enables packet timestamps for socket-queue timeout behavior.

## Port and Listener Construction
- `ports_create_if()` classifies an interface/port as ordinary DNS, TLS, HTTPS/DoH, DNSCrypt, PROXYv2, or DoQ. It rejects unsupported combinations such as PROXYv2 with DNSCrypt/DoH/DoQ and blocks DoQ on port 53.
- `listening_ports_open()` applies config flags for IPv4/IPv6, UDP/TCP, automatic interfaces, extra automatic ports, and explicit interface arrays.
- `resolve_interface_names()` expands interface names to concrete IPv4/IPv6 addresses with scope IDs when `getifaddrs()` is available.
- `listen_create()` converts each `listen_port` into an event `comm_point`, assigns the appropriate SSL context, DNSCrypt buffer, DoQ table, callback, and transport type.

## TCP Stream Handling
- `tcp_req_info_create/delete/clear()` own per-connection pipelined TCP state.
- Open mesh requests are tracked in `tcp_req_open_item`; finished replies are queued in `tcp_req_done_item`.
- `tcp_req_info_handle_readdone()` invokes the worker callback, handles immediate replies, mesh-deferred replies, and connection drops.
- `tcp_req_info_send_reply()` either writes immediately or queues a copied response subject to `stream_wait_max`.
- `tcp_req_info_handle_writedone()` resumes reading or sends the next queued reply.
- A read-half close drops the connection, matching the RFC 7766 behavior noted in comments.

## HTTP/2 DoH Handling
When built with nghttp2, the file registers callbacks for begin-headers, headers, data chunks, frame completion, stream close, recv, and send.
- GET queries are decoded from `?dns=` using base64url, with fallback for non-url base64.
- POST queries are buffered from DATA frames, honoring content-length when present.
- Invalid endpoint/content-type/method/size yields HTTP status responses.
- DNS responses are copied from the shared comm buffer into per-stream response buffers, bounded by `http2_response_buffer_max`.
- Query buffers are globally bounded by `http2_query_buffer_max`.

## DNS-over-QUIC Handling
When built with ngtcp2, this file contains a substantial DoQ implementation:
- `doq_table_create/delete()` own connection, connection-ID, timer, write-list, static-secret, and memory accounting state.
- `doq_conn_create/setup/delete()` create server-side ngtcp2 connections, TLS state, connection IDs, transport parameters, and locks.
- Connection IDs are indexed separately in `conid_tree` so packets with rotated CIDs can find the right connection.
- Timers use an rbtree keyed by timeval, with set-lists for multiple timers at the same instant.
- Streams parse the two-byte DNS-over-TCP-style length prefix, buffer input, call the resolver callback, queue output, and keep output allocated for QUIC retransmission until acknowledged.
- ngtcp2 callbacks handle stream open/data/close/reset/ack, connection ID creation/removal, handshake completion, crypto logging, and random generation.
- `quic_sslctx_create()` builds a TLS 1.3 server context, loads key/certificate/optional client-verify PEM, configures ALPN `doq`, early data, and ngtcp2 crypto provider glue.
- DoQ memory use is bounded through `doq_table_quic_size_available/add/subtract/get()` against `cfg->quic_size`.

## Memory and Concurrency
The file uses global locks for stream wait and HTTP/2 buffer counters, per-DoQ-table read/write locks for connection and CID trees, per-connection locks, and a size lock for DoQ memory accounting. Listener deletion closes commpoints and frees shared buffers; port-list deletion closes sockets and frees stored socket addresses.

## Edge Cases and Risks
- Many features are compile-time optional; fallback stubs warn or return failure for missing nghttp2/ngtcp2/platform support.
- Socket behavior is highly platform-dependent, with many conditional branches for Linux, BSD, Windows, systemd, and OpenSSL variants.
- DoQ code is large and stateful: connection-ID ownership, timer movement between tree/list forms, and retained retransmission buffers are key invariants.
- Buffer accounting must remain balanced on all error paths; the implementation has explicit subtract/free paths for HTTP/2 and DoQ buffers.
- This file is networking/resolver infrastructure rather than filesystem code, but it is in subset A because the complete OpenBSD source tree is in scope.
