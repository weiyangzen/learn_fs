# sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.main.conf

## Purpose

`gpfs.ganesha.main.conf` is the main GPFS split-config fragment. It sets GPFS behavior, core NFS parameters, NFSv4 behavior, directory services, MDCACHE sizing, and export defaults.

## Important APIs, Types, and Functions

It defines `GPFS`, `NFS_Core_Param`, `NFSv4`, `DIRECTORY_SERVICES`, `MDCACHE`, and `Export_Defaults` blocks with many scalar, boolean, list, and enum parameters.

## Control Flow

The fragment enables GPFS trace, disables GPFS grace, enables clustered core mode, allows NFSv3/v4, sets ports and RPC connection/thread limits, configures NFSv4 lease/grace/minor versions, enables idmapping for a domain, sizes MDCACHE, and establishes conservative export defaults such as no access, TCP transports, sys security, root squash, and disabled commit.

## State and Persistence Behavior

Runtime state includes global daemon protocol/transport settings, idmapping behavior, cache sizing thresholds, and defaults inherited by later `EXPORT` blocks. It is intended to be included before export fragments.

## Dependencies and Integration Points

It integrates with GPFS FSAL, NFS core, NFSv4, directory services/idmapping, MDCACHE, and export loaders.

## Risks and Edge Cases

High cache and RPC limits may be inappropriate for small systems. `Access_Type = none` in defaults requires exports to override access. `NFS_Commit = FALSE` changes write durability semantics and must match deployment expectations. Domain name is sample-specific.

## Test Signals

Syntax validation should pass. Runtime tests should inspect effective core settings, idmapping domain, cache thresholds, and export defaults inherited by a sample export.
