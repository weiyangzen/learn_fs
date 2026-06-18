# sources/user-network-fs/samba/source3/lib/messages_ctdb.h

Purpose: declares the CTDB-backed source3 messaging transport API.

Important APIs/types/functions: opaque `messaging_ctdb_fde`, init/destroy/send, event-context registration, active check, and CTDB connection accessor.

Control flow: callers initialize CTDB messaging, register event loops, send cluster messages, and destroy the transport on shutdown.

State/persistence behavior: exposes process-global CTDB connection management and talloc-owned FDE handles.

Dependencies/integration: included by messaging core, CTDB refs, and tests.

Risks/test signals: clustered and non-clustered build coverage plus CTDB messaging tests validate API use.
