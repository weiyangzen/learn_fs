# sources/user-network-fs/samba/source3/rpc_server/epmapper/srv_epmapper.c

Purpose: endpoint mapper RPC server for resolving registered Samba RPC interfaces into endpoint towers through the local `epmdb.tdb` database.

Important APIs/types/functions: `_epm_Lookup`, `_epm_Map`, `_epm_LookupHandleFree`, `build_ep_list`, `build_ep_list_fn`, `build_ep_list_fill_iface`, `epm_map_get_towers`, and `epmapper_init_server`. Internal types include `dcesrv_ep_iface`, `rpc_eps`, and a lookup policy-handle state.

Control flow: initialization opens `lock_path("epmdb.tdb")` read-only. Lookup traverses every TDB record, validates null-terminated syntax-id keys and string-vector endpoint values, parses bindings, substitutes the local IPv4 address for wildcard/non-IP TCP hosts, builds endpoint towers, and stores cursor state in a policy handle. Each call returns up to `max_ents`, advances the in-memory cursor by pointer arithmetic, and closes the handle at exhaustion. Map validates the input tower transfer syntax, infers requested transport, fetches matching bindings for the requested interface, and returns towers similarly.

State/persistence behavior: persistent endpoint data lives in `epmdb.tdb`; per-client lookup/map progress is transient policy-handle state containing a talloc array of towers.

Dependencies/integration: uses TDB/db utilities, DCERPC binding parser/build-tower helpers, tsocket local address detection, generated epmapper NDR, and source3 policy-handle helpers.

Risks/test signals: malformed TDB records are ignored, but version filtering has permissive assignments in exact and major-only branches that may over-match. Tests should cover null-terminated record validation, TCP host substitution, paged lookup handles, map tower validation, unsupported insert/delete/mgmt calls, and empty/exhausted cursor behavior.
