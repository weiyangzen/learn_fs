# sources/user-network-fs/samba/source4/libcli/ldap/ldap_client.c

Purpose: core LDAP client transport, connection, request multiplexing, reconnect, timeout, and error handling.

Important APIs: `ldap4_new_connection()`, `ldap_connect_send()`, `ldap_connect_recv()`, `ldap_connect()`, `ldap_set_reconn_params()`, `ldap_request_send()`, `ldap_request_wait()`, `ldap_result_n()`, `ldap_result_one()`, `ldap_check_response()`, `ldap_errstr()`, and `ldap_transaction()`. Internal helpers parse LDAP URLs, establish TCP/Unix sockets, start TLS/StartTLS, decode PDUs, match replies, and abandon timed-out or destroyed requests.

Control flow: a connection owns raw/TLS/SASL tstreams, a send queue, a single outstanding read subrequest, and a pending request list. Requests are encoded with LDAP control handlers, assigned monotonically increasing message IDs, queued through `tstream_writev_queue_send()`, and added to pending. Reads begin only while pending requests exist; decoded messages are matched by message ID, appended to request replies, and non-search responses complete the request. Search entries and references can accumulate until a done response arrives.

State and persistence: volatile talloc state includes host/port, reconnect URL/counters, active stream, pending requests, last LDAP error string, and timers. Reconnect can synchronously reconnect and rebind after transport errors when enabled.

Dependencies and integration: uses tstream, tevent, Samba sockets, ASN.1/LDAP encoders, TLS, resolver, composite socket connect, loadparm, and LDAP control handlers.

Risks: `ldap_reconnect()` is marked not async safe. Message ID zero fallback maps malformed server replies to the first pending request. Critical undecoded controls convert a request to `LDAP_UNAVAILABLE_CRITICAL_EXTENSION`. Request destructors and timeouts send abandon operations, so lifetime and callback ordering need careful tests. Test signals include LDAP/LDAPS/LDAPI URL parsing including IPv6, StartTLS response validation, reconnect/rebind, multi-entry search, critical unknown controls, timeout abandon, unbind/abandon completion, and connection-dead propagation to pending requests.
