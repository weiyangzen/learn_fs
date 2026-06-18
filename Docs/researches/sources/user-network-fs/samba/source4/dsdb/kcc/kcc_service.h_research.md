# sources/user-network-fs/samba/source4/dsdb/kcc/kcc_service.h

Purpose: shared KCC service state definition and include hub for generated prototypes and KCC maintenance helpers.

Important types/APIs: `struct kccsrv_service` is the central in-memory state object. It stores the `task_server`, `startup_time`, `config_dn`, system session info, local partition DN list, SAMDB connection, immutable local `ntds_guid`, periodic timer state (`interval`, `next_event`, `te`, external-command `subreq`, and status), cleanup timestamps, RODC flag, and `samba_kcc_code`. It forward-declares `struct kcc_connection_list` and includes garbage collection, DNS scavenging, and generated service prototypes.

Control flow/state: this header does not execute logic but defines the mutable state consumed by `kcc_service.c` and `kcc_periodic.c`. The fields split persistent directory state from transient scheduling and throttling: actual topology and tombstones live in DSDB, while this struct caches timestamps and open handles for one task lifetime.

Dependencies/integration: DRSUAPI client NDR types, DSDB common utilities, tombstone and DNS scavenging headers, and generated `kcc_service_proto.h`. Risks are state-coupling risks: missing initialization of timer/timestamp fields changes cleanup cadence, and any new field must respect the service's single-task tevent lifetime. Test signals: startup initializes `config_dn`, `partitions`, `samdb`, `ntds_guid`, RODC status, and periodic timer before IRPC registration.
