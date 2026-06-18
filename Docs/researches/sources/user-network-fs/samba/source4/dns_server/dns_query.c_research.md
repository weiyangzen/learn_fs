# sources/user-network-fs/samba/source4/dns_server/dns_query.c

## Purpose
Processes DNS queries for Samba's internal DNS server. It answers authoritative records from Samba DNS storage, follows CNAMEs with bounded recursion, forwards non-authoritative or CNAME-target queries to configured forwarders, adds authority records, and handles TKEY negotiation for GSS-TSIG.

## Important APIs, types, and functions
- `add_response_rr()` converts `dnsp_DnssrvRpcRecord` values into wire-response `dns_res_rec` records.
- `add_dns_res_rec()` deep-copies forwarded response records into local response arrays.
- `ask_forwarder_send/recv()` wraps asynchronous DNS client forwarding.
- `handle_authoritative_send/recv()` looks up local records and processes each through `handle_dnsrpcrec_send()`.
- `handle_dnsrpcrec_send()` filters record types, emits CNAMEs, and recursively resolves CNAME targets locally or through a forwarder, capped by `MAX_Q_RECURSION_DEPTH`.
- `create_tkey()`, `accept_gss_ticket()`, and `handle_tkey()` implement TKEY negotiation and populate the TKEY store.
- `dns_server_process_query_send/recv()` is the public async query-processing API.

## Control flow
`dns_server_process_query_send()` rejects packets without exactly one question, rejects QCLASS_NONE with NOT_IMPLEMENTED, handles TKEY questions immediately, builds a forwarder list from loadparm, then chooses authoritative handling, recursive forwarding, or NAME_ERROR. Authoritative processing initializes answer and authority arrays, resolves records from LDB-backed DNS helpers, follows CNAMEs for A/AAAA, and adds the zone SOA authority record before completion. Forwarder failures remove the current forwarder from the list and try the next one.

`handle_tkey()` expects the TKEY RR to be the last additional or answer RR. For GSSAPI mode it creates or reuses a TKEY, runs GENSEC update, stores reply key data on success, and marks the request for signing. Unsupported modes return DNS TKEY errors.

## State and persistence behavior
Normal queries do not persist changes. They allocate response arrays on tevent request contexts and move them to the caller in `dns_server_process_query_recv()`. TKEY negotiation mutates the DNS server's in-memory circular TKEY store and stores GENSEC/session state for later TSIG verification/signing.

## Dependencies and integration points
Uses Samba task context, loadparm DNS forwarder settings, DNS client library, DSDB DNS lookup helpers, generated DNS/DNSP NDR types, GENSEC server setup, DLIST list helpers, and tevent asynchronous request patterns. It integrates with `dns_crypto.c` through the shared TKEY store and request-state signing flags.

## Risks and edge cases
- Only one question per query is supported.
- CNAME recursion is silently capped by returning success with no deeper records when depth reaches 20.
- Forwarded additional records are moved in `ask_forwarder_recv()` but not copied into final answers during CNAME forwarded handling; only answers and NS records are copied in that path.
- TKEY delete mode is acknowledged but not implemented.
- `accept_gss_ticket()` maps MORE_PROCESSING_REQUIRED to OK auth error internally, but `handle_tkey()` then sets BADKEY for that status; multi-leg negotiation behavior needs protocol tests.
- Forwarder list handling removes failed entries but does not free with special cleanup beyond talloc ownership.

## Test signals
Needed coverage includes authoritative A/AAAA/CNAME/SRV/SOA/MX/TXT/PTR/NS answers, wildcard lookup, NAME_ERROR with SOA authority, forwarding and multi-forwarder fallback, recursion flags, CNAME local and forwarded resolution, TKEY GSS success/failure/mode handling, and TSIG signing handoff to `dns_crypto.c`.
