# sources/user-network-fs/samba/source3/rpc_server/spoolss/srv_spoolss_nt.h

Purpose: Public internal declarations for the spoolss server implementation in `srv_spoolss_nt.c`. It exposes lifecycle cleanup, printer driver upgrade messaging, and monitored print queue cache refresh hooks to other Samba source3 RPC/server code.

Important APIs: `srv_spoolss_cleanup()` tears down spoolss server state; `do_drv_upgrade_printer()` is a messaging callback taking `messaging_context`, sender `server_id`, message type, and payload `DATA_BLOB`; `update_monitored_printq_cache()` refreshes cached print queue state. The header itself defines no data structures and depends on forward-visible Samba types from included compilation units.

Control flow and state: This file only declares entry points. State is owned by the spoolss implementation and Samba messaging/printing subsystems. `do_drv_upgrade_printer()` integrates with asynchronous server messages, while cache update and cleanup imply process-global spoolss state outside the header.

Dependencies and integration: Consumers must include Samba messaging and RPC type definitions before or via surrounding includes. The functions integrate spoolss with driver upgrade notifications and print queue monitoring, likely called during spoolss server startup/shutdown or messaging dispatch.

Risks and test signals: ABI/signature drift against `srv_spoolss_nt.c` would break build. Useful tests are compile coverage, spoolss startup/shutdown paths, driver upgrade message delivery, and print queue cache refresh behavior after printer configuration changes.
