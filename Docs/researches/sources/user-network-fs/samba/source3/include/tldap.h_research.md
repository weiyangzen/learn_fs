# sources/user-network-fs/samba/source3/include/tldap.h

## Purpose
`tldap.h` declares Samba's tevent/talloc-based asynchronous LDAP client interface. It provides typed LDAP result codes, request/response functions for LDAP protocol operations, message inspection helpers, controls, modifications, debug logging, and constants for LDAP application tags, modification operations, scopes, and paged-results control.

## Important APIs, Types, and Functions
- Opaque state: `struct tldap_context` and `struct tldap_message`.
- Data shapes: `tldap_control`, `tldap_attribute`, and `tldap_mod`.
- Result code abstraction: `TLDAPRC`, `TLDAP_RC`, `TLDAP_RC_V`, `TLDAP_RC_EQUAL`, `TLDAP_RC_IS_SUCCESS`, and many `TLDAP_*` code constants.
- Context/transport: `tldap_context_create_from_plain_stream`, `tldap_context_create`, `tldap_get_plain_tstream`, TLS/gensec stream setters/getters, channel bindings, connection status, and attribute get/set.
- LDAP operations: async send/recv and sync wrappers for SASL bind, simple bind, search, search-all, add, modify, delete, and extended operations.
- Message inspection: `tldap_msg_id`, `tldap_msg_type`, `tldap_msg_rc`, matched DN, diagnostic message, referral, server controls, last message, and `tldap_rc2string`.
- Debug integration: `tldap_set_debug`.

## Control Flow and State
The API follows the Samba async pattern: callers create a `tevent_req` with `*_send`, run it on a `tevent_context`, and complete it with the paired `*_recv`, or call synchronous wrappers that perform the same operation internally. `tevent_req_ldap_error` and `tevent_req_is_ldap_error` encode LDAP result codes into tevent request failure state. The context can wrap a raw fd or tstream and can be upgraded with TLS or GENSEC streams.

## Persistence Behavior
The header itself does not persist data. LDAP add/modify/delete/extended operations can change directory state through their implementations. Context attributes can hold process-local metadata but are not persisted.

## Dependencies and Integration Points
It includes `replace.h`, `talloc.h`, `tevent.h`, and `DATA_BLOB`. It integrates with async Samba authentication/directory code, tstream TLS/GENSEC layers, and higher-level helpers in `tldap_util.h`.

## Risks
- `TLDAPRC` may be an immediate structure on some compilers; callers must use comparison/access macros rather than assuming it is a raw integer.
- Async send/recv pairs require correct talloc ownership and request lifecycle handling.
- TLS/GENSEC stream replacement affects channel bindings and connection security; callers must not use stale plain streams after upgrade.
- Search APIs have size/time/deref controls that can affect directory load and memory usage.

## Test Signals
Async LDAP operation tests, sync wrapper tests, SASL bind continuation handling, TLS/GENSEC upgrade tests, paged search coverage through utilities, and error propagation checks through `tevent_req_is_ldap_error`.
