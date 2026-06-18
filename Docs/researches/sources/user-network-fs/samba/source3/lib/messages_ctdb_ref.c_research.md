# sources/user-network-fs/samba/source3/lib/messages_ctdb_ref.c

Purpose: provides reference-counted CTDB messaging initialization and teardown.

Important APIs/types/functions: `messaging_ctdb_ref()`, `struct msg_ctdb_ref`, `msg_ctdb_ref_recv()`, and `msg_ctdb_ref_destructor()`.

Control flow: first reference or PID change initializes CTDB messaging; each ref registers an event-context FDE and stores callback data. Incoming CTDB messages are forwarded through the receive trampoline. Last destructor destroys CTDB messaging.

State/persistence behavior: static `ctdb_pid` and `refs` track process-local ownership and live references. CTDB daemon registrations exist while refs are live.

Dependencies/integration: used by `messages.c` when clustering is enabled. Depends on `messages_ctdb.h`, ref header, DLIST, talloc, tevent, and debug.

Risks/test signals: fork/PID handling and last-ref teardown are critical. Tests should cover multiple refs, init failure, PID changes, receive callbacks, and final destroy.
