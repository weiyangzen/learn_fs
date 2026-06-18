# sources/user-network-fs/samba/source4/dsdb/repl/drepl_service.c

Purpose: registers and initializes Samba's DSDB replication service task and exposes IRPC handlers for replication, refresh, FSMO, secret replication, and RID allocation triggers.

Important APIs/functions: `server_service_drepl_init()` registers the `drepl` service; `dreplsrv_task_init()` initializes service state; `dreplsrv_connect_samdb()` opens SAMDB, records NTDS GUID/RODC status, and populates DRS bind capabilities; `drepl_replica_sync()` handles forwarded `DsReplicaSync`; `dreplsrv_refresh()` reloads partitions; wrapper handlers forward ReplicaAdd/Del/Mod and secret triggers. `_drepl_schedule_replication()` schedules pull operations and coordinates deferred IRPC replies.

Control flow/state: startup is AD DC-only, then credentials, SAMDB, partitions, periodic timer, pending immediate, notify timer for writable DCs, IRPC names, and message handlers are registered. `drepl_replica_sync()` validates level/NC, finds a partition, decides async vs deferred reply, schedules all or one source DSA by GUID/DNS, creates temporary DSAs when needed, and schedules immediate pull execution. Completion callback counts outstanding operations and replies with the last failure.

Dependencies/integration: task service framework, loadparm, SAMDB/roles, DRSUAPI/IRPC generated interfaces, partition and queue modules, notify/RID/secret/FSMO code, and messaging. Risks include large bind capability surface, deferred reply accounting, temporary source handling, and unimplemented ReplicaAdd/Del/Mod despite registration. Test signals: role gating, bind info negotiation fields, async vs sync `DsReplicaSync`, `DRS_SYNC_ALL`, `DRS_SYNC_BYNAME`, temporary DSA path, refresh after KCC notification, and RODC notify skip.
