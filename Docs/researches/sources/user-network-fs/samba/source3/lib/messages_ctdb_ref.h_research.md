# sources/user-network-fs/samba/source3/lib/messages_ctdb_ref.h

## sources/user-network-fs/samba/source3/lib/messages_ctdb_ref.h

Purpose: Declares the source3 messaging hook used to hold a CTDB messaging reference and receive CTDB-delivered messages.

Important APIs/types/functions: `messaging_ctdb_ref(TALLOC_CTX *, struct tevent_context *, const char *sockname, int timeout, uint64_t unique_id, recv_cb, void *private_data, int *err)` returns an opaque talloc-owned reference. The callback receives the tevent context, raw message bytes, optional file descriptors, and caller-private state.

Control flow: This header only exports the constructor. Callers provide the event loop, CTDB socket name, timeout, unique process id, and receive callback; implementation lifetime is represented by the returned pointer.

State and persistence behavior: State is event-loop and talloc-lifetime based, not file-persistent. The callback boundary can transfer fd state.

Dependencies and integration points: Depends on `replace.h`, `tevent.h`, talloc ownership, and source3 messaging/CTDB integration.

Risks: The API is opaque, so callers must handle NULL returns and `err`. Callback fd ownership and timeout semantics need implementation-level care.

Test signals: CTDB messaging tests should exercise connect failure, timeout, callback dispatch with bytes/fds, and talloc teardown.
