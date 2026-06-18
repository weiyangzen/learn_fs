# sources/user-network-fs/samba/source4/libcli/ldap/ldap_client.h

Purpose: internal LDAP client declarations for connection and request state plus public-ish client helper prototypes.

Important types: `enum ldap_request_state`; `struct ldap_request` with list links, connection pointer, message ID, state, replies, status, encoded data, write iovec, callback, and timeout event; `struct ldap_connection` with raw/TLS/SASL/active streams, send queue, receive subrequest, loadparm, host/port, bind cache, pending list, GENSEC state, timeout, and event context.

Control flow contract: `ldap_request_send()` creates requests that become pending until matched replies, timeout, abandon, or connection death. Search consumers can call `ldap_result_n()` repeatedly. Connect and bind APIs manipulate the connection streams.

State and persistence: all fields are in-memory and talloc-owned. The reconnect block preserves a URL and retry timing in the connection object only.

Dependencies and integration: includes network iovec types and `libcli_ldap.h`; forward declarations tie into GENSEC credentials, loadparm, ldb parse/control types, and composite connect.

Risks: structs expose internals to sibling modules, so invariants such as pending list membership, active stream selection, and timeout event ownership are not encapsulated. Test signals should exercise request state transitions, reply array growth, timeout events, and bind/rebind state.
