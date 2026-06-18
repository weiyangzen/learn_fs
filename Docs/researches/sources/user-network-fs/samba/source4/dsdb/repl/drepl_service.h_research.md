# sources/user-network-fs/samba/source4/dsdb/repl/drepl_service.h

Purpose: central type contract for the DSDB replication service.

Important types/APIs: `dreplsrv_drsuapi_connection` caches DCE/RPC pipe, binding handle, session key, remote bind info, and bind handle. `dreplsrv_out_connection` caches a binding per source host. `dreplsrv_partition_source_dsa` wraps one `repsFrom`/`repsTo` source, its `repsFrom1`, `notify_uSN`, and connection. `dreplsrv_partition` holds NC identity, UDV, source and notify lists, and partial/RODC replica flags. `dreplsrv_out_operation` and `dreplsrv_notify_operation` are queued work items. `dreplsrv_service` aggregates task, credentials, SAMDB, NTDS GUID, bind capabilities, timers/immediate, partitions, connections, operation queues, RID allocation flag, and RODC status.

Control flow/state: this header defines the in-memory model used by all DREPL implementation files. Durable replication state is stored in DSDB attributes and committed objects; this struct holds caches, queues, timers, and transient per-run flags. The callback typedef lets extended operations report asynchronously through the same pull machinery.

Dependencies/integration: generated DRSUAPI client types, IRPC, outgoing helper header, and generated service prototypes. Risks include tight cross-file coupling, single-lane queue assumptions baked into `ops.current`/`n_current`, and lifetime sensitivity of talloc-referenced source DSAs. Test signals: compile coverage for all DREPL modules, queue ownership/lifetime tests, and startup initialization of every field used by periodic, notify, pull, and extended-op paths.
