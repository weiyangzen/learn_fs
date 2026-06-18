# sources/user-network-fs/samba/source3/rpc_server/eventlog/srv_eventlog_reg.h

Purpose: small public header for eventlog registry initialization.

Important APIs/types/functions: declares `bool eventlog_init_winreg(struct messaging_context *msg_ctx);` and guards it with `SRV_EVENTLOG_REG_H`.

Control flow: consumers include this header when they need to initialize the registry backing for eventlog RPC service startup. The main consumer in this subset is `srv_eventlog_nt.c`, which calls the function before invoking generated server initialization.

State/persistence behavior: the header does not own state, but its API implies writes to Samba's registry backend through the implementation.

Dependencies/integration: exposes only `struct messaging_context` by pointer and avoids pulling winreg implementation details into callers.

Risks/test signals: compile coverage should ensure the declaration matches `srv_eventlog_reg.c`. Startup tests for eventlog should indirectly validate the header-level contract.
