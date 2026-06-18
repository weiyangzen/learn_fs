# sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.conf

## Purpose

`gpfs.conf` is a basic GPFS export sample showing GPFS-specific defaults, clustered NFS core settings, NFSv4 lease configuration, and one export.

## Important APIs, Types, and Functions

It uses `EXPORT_DEFAULTS`, `NFS_Core_Param`, `NFSv4`, `GPFS`, and `EXPORT` with nested `FSAL { Name = GPFS; }`.

## Control Flow

The sample sets a long attribute expiration default appropriate for GPFS invalidate upcalls, enables clustered mode, sets NFSv4 lease lifetime to 90, enables read delegations in the `GPFS` block, and exports `/ibm/gpfs0` at matching pseudo path with read/write access.

## State and Persistence Behavior

Runtime persistence lives in GPFS and Ganesha's export/config state. Longer attribute caching relies on GPFS invalidation upcalls for correctness.

## Dependencies and Integration Points

It depends on FSAL_GPFS, NFSv4 configuration, export defaults, and clustered core behavior.

## Risks and Edge Cases

Delegations and long cache lifetimes must match GPFS callback behavior and cluster topology. Export ID 77 and path `/ibm/gpfs0` are placeholders and can conflict or fail if reused unchanged.

## Test Signals

Syntax validation plus GPFS-enabled runtime tests should verify export load, NFSv4 mount, delegation behavior, and cache invalidation under file changes.
