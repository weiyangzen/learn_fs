# sources/user-network-fs/samba/source4/rpc_server/dnsserver/dcerpc_dnsserver.c

Purpose: implements the MS-DNSP DCE/RPC server endpoint. It serves DNS server/zone queries, zone creation/deletion, zone property resets, record enumeration, and record add/update/delete operations against Samba AD DNS data.

Important APIs and control flow: binding requires integrity. `dnsserver_connect()` creates per-connection `dnsserver_state`, opens samdb as the caller, initializes server info, enumerates fixed domain/forest DNS partitions, loads zones, initializes zone info, and caches the state with an interface magic. `dnsserver_query_server()` and `dnsserver_query_zone()` map many named properties to version-specific RPC output types. `dnsserver_operate_server()` implements `ZoneCreate` and validates many other operations as not implemented. `dnsserver_complex_operate_server()` supports property query, zone enumeration, directory partition enumeration, and partition info. `dnsserver_operate_zone()` implements dword property reset and DS zone delete. Enumeration paths search `dnsNode` records, build ordered trees, include optional additional A records, and return NDR-sized `DNS_RPC_RECORDS_ARRAY`. `dnsserver_update_record()` normalizes node names, rejects CNAME self-reference, and dispatches add, update, delete, or empty-node operations to `dnsdb.c`.

State and persistence: keeps cached partition/zone/serverinfo state per connection. Persistent writes happen through `dnsserver_db_create_zone()`, `dnsserver_db_delete_zone()`, `dnsserver_db_do_reset_dword()`, and record DB helpers. `dnsserver_reload_zones()` reconciles cached zones after zone create/delete.

Dependencies and integration: depends on `dnsserver.h`, generated DNS server NDR, common RPC/SAM helpers, AD DNS common utilities, LDB, and dlinklist.

Risks and test signals: many accepted operations return `WERR_CALL_NOT_IMPLEMENTED`; access-control FIXME remains on server configuration queries. Tests should cover client version differences, zone filters, root hints, additional-record expansion, CNAME loop rejection, permission failures, and cache reload after zone mutation.
