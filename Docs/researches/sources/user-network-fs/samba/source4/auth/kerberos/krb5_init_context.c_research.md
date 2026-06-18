<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/krb5_init_context.c -->
# sources/user-network-fs/samba/source4/auth/kerberos/krb5_init_context.c

Purpose: wraps krb5 context initialization and, for Heimdal builds, routes Kerberos KDC network I/O through Samba's tevent/socket stack. It also wires Kerberos logging into Samba debug output and sets embedded Heimdal flags from Samba configuration.

Important APIs and types: `struct smb_krb5_socket` holds socket, fd event, status, request/reply blobs, packet parser, and Heimdal host info. `smb_krb5_init_context_basic()` creates a raw krb5 context, applies Samba krb5.conf/default realm on Heimdal, and registers the send-to-KDC plugin once. `smb_krb5_init_context()` allocates `struct smb_krb5_context`, installs a destructor, initializes logging, and applies embedded Heimdal flags. Heimdal-only `smb_krb5_context_set_event_ctx()` and `_remove_event_ctx()` install and restore tevent-aware KDC send functions.

Control flow: UDP reads use `socket_pending()` then `socket_recv()`. TCP uses Samba packet framing with a 4-byte length prefix and strips that prefix on full packets. `smb_krb5_send_and_recv_func_int()` iterates addrinfo entries, creates UDP or TCP sockets, connects, registers fd events and timeout, sends the request, loops tevent until reply or error, copies reply to krb5 memory, and tries the next address on timeout or network error.

State and persistence: `smb_krb5_context` owns `krb5_context`, optional Heimdal log facility, and current tevent reference. A global `smb_krb5_plugin_db` maps krb5 context pointers to per-context send-to-KDC callback state. Destructors remove plugin records and free krb5/log resources.

Dependencies and integration: depends on Samba socket, packet, tsocket, resolve, param, dbwrap_rbt, Kerberos send_to_kdc plugin APIs, and embedded Heimdal internals when available. It is foundational for all source4 Kerberos code.

Risks and test signals: global plugin registration and pointer-keyed dbwrap state are concurrency-sensitive. Tests should cover nested tevent loops, restoring previous event contexts, UDP/TCP fallback, timeout behavior, KDC unreachable mapping, IPv4/IPv6, config-file precedence, realm setting, logging cleanup, and embedded Heimdal PAC/canonical-client flags. MIT builds bypass most plugin code and need separate coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/krb5_init_context.c -->
