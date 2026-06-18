# sources/user-network-fs/samba/source4/dsdb/kcc/kcc_service.c

Purpose: registers and initializes the KCC task service for AD DCs. It owns startup role gating, SAMDB connection, partition discovery, periodic scheduling, and IRPC entry points for `DsExecuteKCC` and `DsReplicaGetInfo`.

Important APIs/functions: `server_service_kcc_init()` registers the `kcc` service; `kccsrv_task_init()` builds `struct kccsrv_service`; `kccsrv_init_creds()` obtains system session info; `kccsrv_connect_samdb()` opens local SAMDB, records this DC's NTDS GUID, and detects RODC mode; `kccsrv_load_partitions()` reads rootDSE `namingContexts` and `configurationNamingContext`; `kccsrv_execute_kcc()` handles manual KCC execution; `kccsrv_replica_get_info()` forwards to `kccdrs_replica_get_info()`.

Control flow/state: the task refuses standalone and domain-member roles, then initializes credentials, SAMDB, partition list, loadparm-driven periodic intervals, and `samba_kcc_code`. Manual `DsExecuteKCC` either runs `kccsrv_simple_update()` synchronously or starts `samba_runcmd_send()` and optionally defers the IRPC reply until `manual_samba_kcc_done()`. Persistent state is not directly stored here, but startup populates service fields consumed by periodic code.

Dependencies/integration: Samba task service framework, loadparm, IRPC generated DRSUAPI handlers, SAMDB helpers, roles library, and `kcc_periodic.c`. Risks include fatal task termination on startup failures, manual command concurrency returning `NT_STATUS_DS_BUSY`, and partition list loading only from rootDSE naming contexts. Test signals: AD DC-only startup, `kccsrv:samba_kcc` true/false paths, async/sync `DsExecuteKCC`, and failure behavior when SAMDB lacks NTDS metadata.
