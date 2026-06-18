# sources/user-network-fs/samba/source3/libsmb/namequery.c

## Purpose
This is Samba's libsmb name-resolution engine. It resolves names through direct IP parsing, local name cache, DNS/hosts, ADS DNS SRV records, LMHOSTS, WINS, NetBIOS broadcast, and domain-controller/KDC helper flows. It also implements async NetBIOS node status and name query transactions over UDP, optionally racing replies from `nmbd`'s unexpected-packet reader.

## Important APIs, Types, And Functions
Exported APIs include SAF cache helpers (`saf_store`, `saf_join_store`, `saf_delete`, `saf_fetch`), node status APIs (`node_status_query_send/recv`, `node_status_query`, `name_status_find`), NetBIOS name query APIs (`name_query_send/recv`, `name_query`), broadcast and WINS APIs (`name_resolve_bcast_send/recv`, `name_resolve_bcast`, `resolve_wins_send/recv`, `resolve_wins`), general resolution APIs (`internal_resolve_name`, `resolve_name`, `resolve_name_list`), and DC helpers (`find_master_ip`, `get_pdc_ip`, `get_sorted_dc_list`, `get_kdc_list`).

Key async state structs are `sock_packet_read_state`, `nb_trans_state`, `node_status_query_state`, `name_query_state`, `name_queries_state`, `query_wins_list_state`, `resolve_wins_state`, and `name_resolve_bcast_state`. The file-level `global_in_nmbd` flag lets nmbd avoid querying itself as WINS.

## Control Flow
Low-level NetBIOS transactions are built around `nb_trans_send`: bind a UDP datagram socket, try to attach an `nb_packet_reader` for packets captured by nmbd, send the packet, resend every second, and complete when `sock_packet_read_send` receives a matching packet from either path. `sock_packet_read_got_socket` parses UDP packets with `parse_packet_talloc`, filters by transaction ID, and applies a caller validator. Validators parse node status and name-query response semantics.

`node_status_query_send` builds a question type `0x21` request and waits up to ten seconds. `name_status_find` first checks the status cache, then LMHOSTS, then node status, storing successful non-`0x1c` results. `name_query_send` builds a question type `0x20` request, collects positive address records, handles negative WINS responses as `NT_STATUS_NOT_FOUND`, accumulates broadcast replies until timeout, sorts addresses by interface proximity, and returns flags.

Higher-level resolution starts in `internal_resolve_name`. It returns direct numeric IPs immediately, then tries `namecache_fetch`, then walks the configured resolve order. `host/hosts` calls `getaddrinfo`, `ads` and `kdc` perform DNS SRV lookups, `lmhosts` reads LMHOSTS, `wins` queries configured WINS tags, and `bcast` broadcasts to IPv4 interface broadcast addresses. Successful results are converted to `struct samba_sockaddr`, deduplicated, cached, and returned.

DC/KDC helpers layer policy on top of `internal_resolve_name`. `get_dc_list` combines server affinity, `password server`, wildcard auto lookup, ADS-only/KDC-only modes, negative connection-cache filtering, duplicate removal, IPv4 prioritization, and ordered-vs-sortable result handling. `get_sorted_dc_list` retries without a site when the site-specific lookup finds no logon servers.

## State And Persistence
Persistent local state is stored in `gencache` through SAF keys and the name cache. SAF keys prefer recently successful DCs (`SAF/DOMAIN/<domain>`) and join DCs (`SAFJOIN/DOMAIN/<domain>`) with configurable TTLs. Name resolution stores positive name results through `namecache_store`. WINS failures are recorded through `wins_srv_died`, and DC candidates are filtered through the negative connection cache. Runtime state is primarily talloc-owned tevent request state and temporary arrays.

## Dependencies And Integration Points
This file depends on tevent, async socket/tdgram helpers, `libsmb/nmblib` packet builders/parsers, `libsmb/unexpected` packet reader support, LMHOSTS parsing, WINS server configuration, interface enumeration, ADS DNS query helpers, sitename cache, `gencache`, negative connection cache, loadparm settings, and socket/address utility functions. It is declared by `namequery.h` and used by client connection, domain-controller discovery, browser lookup, and password-change workflows.

## Risks And Edge Cases
NetBIOS node status and name queries are IPv4-only; IPv6 names can be returned by DNS/hosts but not by NBT. Async transactions intentionally retry until a matching response or timeout, so wrong validators can spin until timeout. Broadcast queries treat timeout as success if any reply was accumulated. Long names or dotted names skip NBT methods. Cache hits bypass resolver-order changes until expiry. ADS SRV results are already priority/weight ordered, but later sorting is applied only when a list is not considered ordered. Several loops include overflow checks, but many behaviors rely on small configured server/interface lists.

## Test Signals
Useful signals include direct IP resolution, cache hit/miss/expiry, disabled-NetBIOS paths, long and dotted names filtering NBT, WINS negative responses, dead-WINS retry behavior, broadcast multi-interface lookup, LMHOSTS status lookup, node status parsing with MAC extra data, ADS SRV DC/KDC lookup with site fallback, `password server` wildcard and explicit server ordering, negative connection-cache filtering, IPv4 preference for DCs, and tevent timeout behavior for no-response networks.
