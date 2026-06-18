# sources/user-network-fs/nfs-ganesha/src/include/xprt_handler.h

## Purpose
This header defines custom transport data used to associate RPC transports with NFSv4.1 sessions and connection-manager state.

## Important APIs, Types, And Control Flow
`nfs41_session_list_entry_t` links a session into a transport list. `nfs41_sessions_holder_t` contains an rwlock, session list, and session count. `xprt_custom_data_status_t` tracks associated, dissociated, and destroyed states. `xprt_custom_data_t` combines the session holder, status, and managed connection. Functions initialize, destroy, dissociate custom data, and add/remove NFSv4.1 sessions for an `SVCXPRT`.

## State And Persistence
Custom data is attached to live transport objects and tracks session associations and managed connection lifecycle. It is volatile in-memory state.

## Dependencies And Integration Points
It depends on `gsh_rpc.h`, `sal_data.h`, and `connection_manager.h`. It integrates the RPC transport layer with SAL session tracking, connection teardown, and `sal_metrics` transport status metrics.

## Risks And Test Signals
Transport teardown races are the main risk: sessions can outlive, dissociate from, or observe destroyed xprts. Tests should cover session add/remove concurrency, transport destruction with active sessions, denied association paths, connection-manager cleanup, and metrics label updates.
