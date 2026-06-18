# File Research: sources/virtualization/spdk/lib/iscsi/iscsi_rpc.c

Full-file read: 1600 lines.

This file registers and implements SPDK JSON-RPC methods for the iSCSI subsystem. It is mostly RPC glue: decode request objects, validate parameters, call iSCSI subsystem helpers, free generated RPC context allocations, and send JSON-RPC boolean/result/error responses.

Main responsibilities:
- Initiator group RPCs: get/create/delete groups and add/remove initiators/netmasks.
- Target node RPCs: get/create/delete targets, add/remove portal-group/initiator-group maps, add LUNs, configure auth, configure redirection, request logout, enable/read histograms.
- Portal group RPCs: get/create/delete/start portal groups and set portal-group CHAP auth.
- Auth group RPCs: create/delete CHAP groups and add/remove secrets.
- Option/stat RPCs: get/set iSCSI options, set discovery auth, enumerate connections, and aggregate connection states.

Important control flow:
- `SPDK_RPC_REGISTER` exposes methods with either `SPDK_RPC_RUNTIME` or `SPDK_RPC_STARTUP`.
- Most handlers use generated decoder/free helpers from `spdk_internal/rpc_autogen.h`.
- Target deletion is asynchronous: it heap-allocates context, calls `iscsi_shutdown_tgt_node_by_name`, and responds from `rpc_iscsi_delete_target_node_done`.
- `iscsi_get_connections` and `iscsi_get_stats` use `spdk_for_each_channel(&g_iscsi, ...)` to inspect every iSCSI poll group.
- Histogram enablement may run on the target poll-group thread and uses `target->num_active_conns` as a temporary lifetime guard.

Integration points:
- Depends heavily on `iscsi_subsystem.c`, `portal_grp.c`, `init_grp.c`, `tgt_node.c`, `conn.c`, SPDK JSON, RPC, base64, and histogram APIs.
- `iscsi_set_options` initializes `g_spdk_iscsi_opts` before subsystem startup and is intentionally single-use.
- JSON config dumping elsewhere must match these method names and parameter shapes.

Risks and review notes:
- Many invalid states collapse to generic `SPDK_JSONRPC_ERROR_INVALID_PARAMS`, so client diagnostics are limited.
- Several mutations find global objects without consistently holding `g_iscsi.mutex`; correctness depends on RPC/threading assumptions in the broader subsystem.
- `iscsi_get_histogram` reads `target->histogram` without the same target mutex choreography used by enablement.
- `iscsi_set_options` relies on `spdk_json_decode_string` freeing pre-existing default strings before reassignment; this is documented in-line and should be preserved carefully.

Testing focus:
- RPC decode failures, duplicate/missing required fields, and optional defaults.
- Target deletion while connections are active.
- Portal creation rollback on partial failure.
- Histogram enable/get/disable across active and inactive targets.
