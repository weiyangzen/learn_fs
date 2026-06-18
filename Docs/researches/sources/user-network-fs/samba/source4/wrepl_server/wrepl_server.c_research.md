# sources/user-network-fs/samba/source4/wrepl_server/wrepl_server.c

Source read signal: reviewed complete local file (558 lines, 15982 bytes).

## Purpose
`wrepl_server.c` is the Samba4 WINS Replication service bootstrap and shared partner/table management implementation. It opens the local WINS database and WREPL configuration database, loads configured replication partners, builds the owner/version table from existing WINS records, schedules pull and push processing, starts the inbound replication listener, and registers the task as the `wrepl` server service.

## Important APIs, types, and functions
Key local helpers are `wins_config_db_connect()`, `wins_config_db_get_seqnumber()`, `wreplsrv_open_winsdb()`, `wreplsrv_find_attr_as_uint32()`, `wreplsrv_load_partners()`, `wreplsrv_load_table()`, `wreplsrv_setup_partners()`, `wreplsrv_setup_sockets()`, `wreplsrv_task_init()`, and `server_service_wrepl_init()`. Exported service helpers include `wreplsrv_find_partner()`, `wreplsrv_fill_wrepl_table()`, `wreplsrv_find_owner()`, and `wreplsrv_add_table()`. The code fills `struct wreplsrv_service`, `struct wreplsrv_partner`, and `struct wreplsrv_owner` fields declared in the companion header and hands off protocol work to the other WREPL server modules through generated prototypes.

## Control flow
`server_service_wrepl_init()` registers a non-preforking service whose `task_init` is `wreplsrv_task_init()`. Startup rejects hosts that are not configured as WINS servers, allocates `struct wreplsrv_service`, opens `wins.ldb` with a local-owner address selected from `winsdb:local_owner` or the first IPv4 interface, opens `wins_config.ldb`, reads interval defaults from `wreplsrv:*` smb.conf parameters, loads partners, loads the WINS owner table, sets up pull/push timers, listens on WREPL sockets from `dcerpc_endpoint_servers:winsrepl`, starts periodic scavenging/maintenance, and registers the IRPC name `wrepl_server`.

## State and persistence
Persistent state lives in `wins.ldb` and `wins_config.ldb`. The in-memory service caches the configuration database sequence number, partner linked list, owner table, local owner pointer, timers, incoming connections, and scavenging flags. `wreplsrv_load_partners()` uses `@BASEINFO sequenceNumber` to skip reloads when partner configuration has not changed, disables existing partners before reapplying database rows, and forces pull rescheduling when an existing partner is updated. `wreplsrv_add_table()` may advance the local WINS max version in the database when a higher local version is observed.

## Dependencies and integration points
The file depends on Samba task services, talloc, tevent, LDB, the WINS database API, generated `winsrepl` NDR types, `dlinklist`, IRPC messaging, auth/system sessions, loadparm, network interface discovery, and WREPL helper modules for socket, periodic, pull, push, and scavenging behavior. It integrates with `source4/wscript_build` through the `service_wrepl` module and with `wrepl_server/wscript_build` for the private `WREPL_SRV` subsystem.

## Risks
Partner parsing is trust-boundary adjacent: malformed LDB values fall back or fail, and `wreplsrv_find_attr_as_uint32()` accepts decimal and hex forms through signed/unsigned conversions. The configuration reload path marks all partners disabled first, so a partial failure leaves old in-memory partner objects with `type = NONE` until a later successful reload. Local-owner selection depends on interface ordering when `winsdb:local_owner` is absent. `wreplsrv_load_table()` scans all WINS records and updates max-version state; database corruption or unexpected owner/version values can affect replication decisions. Socket setup requires exactly one valid WINSREPL endpoint server.

## Test signals
Useful tests cover startup when WINS is disabled, absent or invalid `wins_config.ldb`, partner sequence-number no-op reloads, add/update/remove partner rows, decimal and hex partner type parsing, `0.0.0.0` owner normalization, local max-version advancement, endpoint configuration errors, and scheduled pull/push/periodic events after startup.
