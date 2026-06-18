# File Research: sources/virtualization/spdk/lib/iscsi/tgt_node.h

Full-file read: 126 lines.

This header defines target-node mapping structures and public target-node APIs.

Main contents:
- `struct spdk_iscsi_ig_map` maps one initiator group into a portal-group map.
- `struct spdk_iscsi_pg_map` maps one portal group, owns initiator-group maps, and stores redirect host/port.
- `struct spdk_iscsi_tgt_node` stores name/alias, mutex, CHAP/digest settings, queue depth, SCSI device, active connection tracking, portal-group maps, destruct callback state, and histogram pointer.
- Declares target construction, shutdown, access checks, map mutation, redirect checks, LUN addition, CHAP updates, JSON output, and histogram enablement.

Integration points:
- Central internal API for RPC, login/discovery, connection cleanup, and subsystem shutdown.

Risks and review notes:
- Public functions return mixed conventions: `bool`, `int`, pointer, and callback completion; callers must handle each carefully.
- `num_active_conns` and `pg` are used for lifetime/thread coordination during histogram and destruction paths.

Testing focus:
- Header/API consumers compile against structure changes.
- Lifetime-sensitive fields during target deletion and histogram operations.
