# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/listen_dnsport.h

## Role

Declares the service-facing listener API for Unbound/unwind DNS client ingress. It covers shared listening sockets, per-worker comm points, UDP/TCP/TLS/HTTP/2/DoQ listeners, TCP pipelining reply bookkeeping, socket creation helpers, DSCP setup, and conditional DNS-over-QUIC state structures.

## Main Types

- `struct listen_dnsport`: per-thread listener container with event base, shared UDP buffer, optional DNSCrypt UDP buffer, and linked comm point list.
- `struct listen_list`: singly linked list of `comm_point` listener events.
- `enum listen_type`: listener transport discriminator for UDP, TCP, ancillary UDP, TLS, DNSCrypt variants, HTTP over TLS, and DoQ.
- `struct unbound_socket`: startup socket metadata: address, descriptor, family, and ACL.
- `struct listen_port`: shared opened listener port list, including fd, transport type, PROXYv2 flag, and `unbound_socket`.
- `struct tcp_req_info`: tracks outstanding and completed DNS requests over one TCP/TLS channel, including open mesh states and queued response buffers.
- `struct tcp_req_open_item` / `struct tcp_req_done_item`: linked-list entries for outstanding mesh references and completed wire responses.
- Conditional `struct doq_table`, `doq_timer`, `doq_conn_key`, `doq_conn`, `doq_conid`, and `doq_stream`: QUIC/DoQ shared connection table, timers, connection IDs, connection state, and per-stream input/output buffers.

## Public API Surface

- Listener lifecycle: `listening_ports_open`, `listening_ports_free`, `listen_create`, `listen_delete`, `listen_setup_locks`, `listen_desetup_locks`, `listen_list_delete`, `listen_get_mem`.
- Listener flow control: `listen_stop_accept`, `listen_start_accept`.
- Socket helpers: `create_udp_sock`, `create_tcp_accept_sock`, `create_local_accept_sock`, `resolve_interface_names`, `set_ip_dscp`, `verbose_print_unbound_socket`.
- TCP multiplexing helpers: `tcp_req_info_create`, `tcp_req_info_delete`, `tcp_req_info_clear`, `tcp_req_info_remove_mesh_state`, `tcp_req_info_handle_writedone`, `tcp_req_info_handle_readdone`, `tcp_req_info_add_meshstate`, `tcp_req_info_send_reply`, `tcp_req_info_handle_read_close`, stream buffer accounting helpers.
- HTTP/2 helpers under `HAVE_NGHTTP2`: callback creation, stream cleanup, and DNS response submission.
- DoQ helpers under `HAVE_NGTCP2`: SSL context/table lifecycle, connection/stream create-delete, rb-tree comparators, connection ID association, packet receive/write/close, timer tree/list manipulation, write-interest lists, QUIC buffer accounting, and test client callbacks.

## Important Behavior and Dependencies

- The header is transport glue between network event code (`util/netevent.h`), ACLs, worker callbacks, mesh state replies, TCP connection limit lists, dnstap, TLS contexts, HTTP/2, and QUIC/ngtcp2.
- UDP uses a shared packet buffer because a datagram is processed one at a time per listener context.
- TCP/TLS request state is explicit because multiple outstanding DNS queries may exist on a single channel and replies may complete out of order.
- DoQ support is guarded by compile-time feature macros and uses rbtrees plus locks for connection lookup by endpoint/DCID and by connection ID.

## Research Notes

- This file is declaration-only; implementation details live in corresponding listener/network service C files.
- The DoQ declarations are substantial and include concurrency-sensitive shared table state, buffer accounting, timer multiplexing, and write-interest lists.
- Socket creation helpers expose platform-sensitive options such as `SO_REUSEPORT`, transparent bind, freebind, systemd socket activation, MSS, TCP_NODELAY/QUICKACK, and DSCP.
