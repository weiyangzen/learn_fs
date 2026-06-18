<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap.c -->
# sources/user-network-fs/samba/source3/lib/tldap.c

## Purpose
`tldap.c` implements Samba's async LDAP client core on top of `tevent`, `tstream`, talloc, and Samba ASN.1 helpers. It owns LDAP context lifecycle, message ID allocation, plain/TLS/GENSEC stream switching, pending request tracking, request encoding, response dispatch, LDAP filter parsing, bind/search/add/modify/delete/extended operations, and synchronous wrappers.

## Important APIs, types, and functions
Key state is `struct tldap_context`, which stores LDAP version, plain/tls/gensec/active streams, outgoing write queue, pending request array, active read request, last synchronous response, debug callback, and context attributes. `struct tldap_message` holds decoded response state, entry attributes, result codes, diagnostic strings, SASL credentials, extended response data, and controls. Public helpers include `tldap_context_create`, `tldap_context_create_from_plain_stream`, `tldap_connection_ok`, stream accessors/setters, context attributes, `tldap_sasl_bind[_send/_recv]`, `tldap_simple_bind`, `tldap_search[_send/_recv]`, `tldap_search_all_send`, `tldap_add`, `tldap_modify`, `tldap_delete`, `tldap_extended`, entry accessors, response metadata accessors, and `tldap_rc2string`.

## Control flow
Outbound operations call `tldap_req_create` to start an LDAPMessage sequence and assign a message ID. The operation-specific encoder writes the LDAP protocol payload and delegates to `tldap_msg_send`, which appends controls, serializes ASN.1, puts the request in `ld->pending`, and queues a write on `ld->active`. The first pending request starts a packet read. `read_ldap_more` peeks ASN.1 sequence length so `tstream_read_packet_send` reads whole LDAP PDUs. `tldap_msg_received` parses message ID/type, finds the matching pending request, moves the ASN.1 data into that request, completes it, and starts the next read while pending requests remain. Search is multi-step: entries and references re-register the subrequest as pending and notify the caller, while the final result decodes LDAPResult and controls.

## State and persistence behavior
All state is in-memory and scoped to the talloc hierarchy. Stream upgrades replace the active transport and free old TLS/GENSEC wrappers as needed. Disconnect tears down streams, stops the outgoing queue, cancels the read request, and completes all pending requests with an LDAP error. Synchronous wrappers create a temporary event context, poll the async operation, then save the final result in `ld->last_msg` for diagnostic retrieval.

## Dependencies and integration points
The file depends on Samba's ASN.1 codec, `tevent_req`, `tevent_queue`, `tstream` BSD/TLS/GENSEC streams, talloc stack frames, NT status helpers, and Samba charset/string helpers. It is the foundation used by `tldap_util.c`, TLS connect, GENSEC bind, LDAP tests, passdb, AD, and client code that needs LDAP without libldap.

## Risks and edge cases
Risk concentrates in ASN.1 length parsing, pending request cleanup, message ID routing, and filter escaping. Unexpected message ID zero or malformed packets disconnect all requests because the client cannot safely attribute the response. Filter parsing is intentionally strict, disallowing whitespace outside values and validating attribute descriptions, escapes, substring rules, extensible match forms, and empty AND/OR filters. Synchronous search returns `TLDAP_BUSY` if async requests are already pending. The `cctrls` client-control parameters are accepted by several APIs but not materially used in this implementation.

## Test signals
`source3/lib/test_tldap.c` is the adjacent focused test file for filter encoding, request/response behavior, and LDAP result handling. Higher-level LDAP bind/search code indirectly tests stream switching, controls, and sync wrappers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/tldap.c -->
