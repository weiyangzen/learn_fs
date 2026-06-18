# sources/user-network-fs/samba/source4/dns_server/dns_server.h

## Purpose
`dns_server.h` declares the internal DNS server's shared runtime structures and module-facing APIs. It connects transport startup, query processing, dynamic updates, directory lookup/replacement helpers, zone authority helpers, DNS-name-to-DN mapping, and TSIG/TKEY support.

## Important APIs, Types, and Functions
- `struct dns_server_tkey` stores negotiated TKEY/TSIG security context: key name, mode, algorithm, session info, GENSEC context, and completion state.
- `struct dns_server_tkey_store` is a fixed-size ring of TKEY pointers with `next_idx`.
- `struct dns_server` owns service task, `samdb`, zone list, TKEY store, and DNS server credentials.
- `struct dns_request_state` carries per-request flags, authenticated/signing state, key name, TSIG record, TSIG error, and local/remote socket addresses.
- Query API: `dns_server_process_query_send()` and `dns_server_process_query_recv()`.
- Update API: `dns_server_process_update()`.
- Directory APIs: `dns_lookup_records()`, `dns_lookup_records_wildcard()`, `dns_replace_records()`, `dns_name2dn()`.
- Authority/security APIs: `dns_authoritative_for_zone()`, `dns_get_authoritative_zone()`, `dns_find_tkey()`, `dns_verify_tsig()`, `dns_sign_tsig()`.

## Control Flow
This header defines contracts rather than executing logic. The transport layer fills `dns_request_state`, query/update handlers consume it, TSIG verification may mark it authenticated and requiring response signing, and helper functions map DNS names to AD-backed record operations.

## State and Persistence
No persistence is implemented in the header, but it establishes ownership: process-wide DNS state lives in `struct dns_server`, per-request mutable state lives in `struct dns_request_state`, and persistent records are reached through the declared `samdb` helper APIs.

## Dependencies and Integration Points
It depends on generated DNS/DNSP NDR types, `dnsserver_common.h`, Samba task and credential types through forward declarations/included headers, `tsocket_address`, and DNS crypto/query/update implementations.

## Risks and Edge Cases
- `DNS_MAX_UDP_PACKET_LENGTH` is fixed at 1232 because EDNS(0) is unsupported; adding EDNS support must revisit callers.
- `TKEY_BUFFER_SIZE` is fixed at 128 and does not expose policy details; high churn of authenticated updates could evict keys unexpectedly.
- The header includes `dnsserver_common.h` twice through two paths, which is protected by guards but indicates historical include layering.

## Test Signals
Compile-time coverage comes from all DNS modules that include the header. Behavioral coverage should focus on request state transitions after TSIG verification, UDP size behavior, TKEY lookup/eviction, query/update APIs, and callers that rely on authoritative zone helpers.
