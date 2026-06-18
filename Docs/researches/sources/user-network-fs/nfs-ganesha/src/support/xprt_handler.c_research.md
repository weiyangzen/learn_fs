# sources/user-network-fs/nfs-ganesha/src/support/xprt_handler.c

Purpose: manages `SVCXPRT` custom data used to track NFSv4.1 sessions associated with a transport and cleanly dissociate sessions during transport destruction.

Important APIs, types, and functions: entry points are `init_custom_data_for_xprt`, `add_nfs41_session_to_xprt`, `remove_nfs41_session_from_xprt`, `dissociate_custom_data_from_xprt`, and `destroy_custom_data_for_destroyed_xprt`. It uses `xprt_custom_data_t`, `nfs41_sessions_holder_t`, and `nfs41_session_list_entry_t`.

Control flow: initialization allocates `xp_u1`, initializes the session list/rwlock, and marks status associated. Add allocates a list entry and increments session ref before taking the lock, then denies association if the xprt is already dissociating. Remove scans the list, drops matching session refs, and updates the count. Dissociation splices the whole session list into a duplicate list under lock, marks the xprt data dissociated, then outside the lock destroys backchannels and removes session connections to avoid lock-order deadlocks. Final destroy asserts the xprt is destroyed and the list is empty, destroys the rwlock, frees custom data, and clears `xp_u1`.

State and persistence: all state is in-memory and attached to `SVCXPRT->xp_u1`. Status transitions are `ASSOCIATED_TO_XPRT`, `DISSOCIATED_FROM_XPRT`, and `DESTROYED`. Session refs are balanced on add/remove/dissociate.

Dependencies and integration points: integrates with SAL session functions, xprt tracepoints, display helpers, Ganesha list utilities, metrics, and RPC transport lifecycle.

Risks: correctness depends on all association paths checking dissociation status before adding sessions. Duplicate entries are possible if callers fail to verify non-association before `add_nfs41_session_to_xprt`. `num_sessions` is a `uint8_t`, so extreme numbers of sessions would wrap. The teardown path uses asserts heavily and assumes exact lifecycle ordering.

Test signals: valuable tests would simulate add/remove, add during dissociation denial, duplicate add behavior, dissociation lock ordering, refcount balance, and final destroy assertions.
