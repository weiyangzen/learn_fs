# sources/user-network-fs/nfs-ganesha/src/include/gsh_config.h

Purpose: This header defines the global NFS-Ganesha configuration model and defaults for core protocol service, RPC/TIRPC, duplicate request caches, NFSv4, recovery, directory services, metrics, and optional protocol features.

Important APIs/types/functions: `enum protos` enumerates enabled RPC programs by compile-time feature. Defaults cover NFS/RQUOTA/RDMA ports, worker counts, DRC sizing, buffers, monitoring, NFSv4 lease/grace, and identity mapping. `nfs_core_parameter_t`, `nfs_version4_parameter_t`, `directory_services_param_t`, and `nfs_parameter_t` make up global `nfs_param`. Macros `NFS_pcp`, `NFS_options`, and `NFS_program` provide shorthand access.

Control flow: Startup populates `nfs_param` defaults, config parsing updates fields, and runtime subsystems read the global settings to bind sockets, size caches, select protocols, enable stats, configure idmapping, recovery, pNFS, RDMA, DBus heartbeat, and memory trimming.

State and persistence: The structs hold daemon-wide persistent runtime configuration. NFSv4 lease/grace/recovery fields and recovery backend settings directly affect client state recovery after restart or failover.

Dependencies and integration points: Includes `nfs4.h`, `gsh_recovery.h`, and password/name service wrappers. Conditional fields integrate with NLM, RQUOTA, NFSACL, RDMA, GSSAPI, and monitoring builds.

Risks: Compile-time conditionals change struct layout. Defaults can materially affect correctness, especially DRC sizing/checksums, grace behavior, idmapping, delegation/pNFS flags, and connection management. Global mutable config requires careful reload/update handling.

Test signals: Validate default initialization, config parser coverage for each stanza, reload behavior, protocol enable masks, DRC bounds, NFSv4 grace/lease recovery, idmapping cache limits, RDMA version masks, DBus heartbeat prefixing, and metrics toggles.
