# sources/user-network-fs/samba/source3/lib/messages.c

Purpose: implements source3 internal process messaging over local datagram sockets and optional CTDB cluster transport.

Important APIs/types/functions: `struct messaging_context`, init/reinit/server-id APIs, register/deregister, send variants, send-all, filtered/read tevent requests, cleanup, parent cleanup job, and names-db access.

Control flow: initialization creates lock/socket directories, opens datagram and optional CTDB transports, initializes server-id DB, and registers built-in handlers. Incoming messages decode headers, ignore self-sends, dispatch to classic callbacks or async waiters, and repost from nested event contexts when needed. Sending handles self-posting, cluster routing, local datagram send, root retry, and errno normalization.

State/persistence behavior: context owns callbacks, waiters, posted messages, event-context registrations, per-process transports, and server-id DB. Socket/lock directories and cleanup are persistent filesystem effects.

Dependencies/integration: depends on tevent, messages_dgm, messages_ctdb, CTDB, server-id DB, loadparm paths, background jobs, and debug/talloc/dmalloc registration. Underpins dbwrap watch, g_lock, and id-cache invalidation.

Risks/test signals: fd ownership, waiter mutation during dispatch, fork reinit, nested contexts, and cluster routing are high risk. Tests include messaging read/fd/send-all, CTDB tests, and indirect dbwrap/g_lock tests.
