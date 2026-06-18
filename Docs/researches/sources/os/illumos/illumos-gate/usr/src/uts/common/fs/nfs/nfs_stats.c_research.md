# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_stats.c

## Purpose
Defines and initializes the per-zone NFS kstats consumed by `nfsstat(8)` for NFS client, server, and ACL procedure accounting across NFSv2, NFSv3, and NFSv4.

## Key Elements
`nfsstat_zone_init_common` allocates a writable virtual named-kstat data block from a template and installs it in a specific zone. `nfsstat_zone_fini_common` removes those kstats by module/version/name. Templates enumerate server totals (`calls`, `badcalls`, referrals), NFSv2/v3/v4 client request counters, NFSv2/v3/v4 server procedure counters, and ACL request/procedure counters.

`nfsstat_zone_init` and `nfsstat_zone_fini` manage client-side per-zone `struct nfs_stats` data for all protocol versions. `rfs_stat_zone_init` and `rfs_stat_zone_fini` manage server-side per-zone `nfs_server`, `rfsproccnt_v2`, `rfsproccnt_v3`, `rfsproccnt_v4`, `aclproccnt_v2`, and `aclproccnt_v3` kstats stored in `nfs_globals_t`.

## Dependencies
Uses illumos kstat APIs, zone IDs, kernel memory allocation, `nfs/nfs.h`, and NFSv4 protocol definitions for the NFSv4 operation list.

## Behavior/Risks
The order and size of each template are ABI-like for tools reading named kstats. Adding, removing, or reordering entries can affect `nfsstat` output and any consumers expecting existing names. The helper returns allocated kstat data even if `kstat_create_zone` fails, and fini paths unconditionally free the corresponding template-sized allocations, so init/fini pairing must remain exact.
