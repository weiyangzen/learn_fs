# sources/user-network-fs/samba/source3/lib/messages_ctdb.c

Purpose: bridges source3 messaging to CTDB for clustered Samba nodes.

Important APIs/types/functions: `messaging_ctdb_init()`, `messaging_ctdb_destroy()`, `messaging_ctdb_send()`, tevent-context registration, active check, and CTDB connection accessor.

Control flow: init opens a CTDB daemon connection for a unique messaging id and receive callback. Send forwards iovecs to destination VNN/server id. Registered event contexts attach CTDB readability handling to tevent loops.

State/persistence behavior: `global_ctdb_context` is process-global transport state; CTDB daemon registrations exist while it is active.

Dependencies/integration: used by `messages.c` under clustering. Depends on CTDB connection helpers, SRVID constants, cluster support, server IDs, and tevent.

Risks/test signals: global lifetime, event-context registration, and cluster send failure handling are risks. CTDB messaging tests validate behavior.
