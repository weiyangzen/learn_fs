# File Research: sources/os/linux/linux-stable/fs/afs/afs_vl.h

This header defines AFS and YFS Volume Location service constants, operation IDs, error codes, VLDB record layouts, and VL address XDR structures.

Major contents:
- Defines VL service port 7003, AFS VL service ID 52, and YFS VL service ID 2503.
- Enumerates VL operations for lookup by ID/name, probing, UUID-based lookup, address lookup, YFS endpoint/cell-name lookup, and capabilities.
- Defines VL error codes covering duplicate IDs/names, no entry, bad names, bad servers, permission errors, memory errors, and release state errors.
- Defines YFS server and endpoint selector constants.
- Defines `YFS_MAXENDPOINTS`.

VLDB records:
- `struct afs_vldbentry` models legacy VLDB entries with volume name, volume type, server count, clone ID, flags, type-specific volume IDs, and up to eight server/partition/flag records.
- Server flags indicate RW/RO/BACK volume placement, UUID references, new replication site, and do-not-use status.
- `AFS_VLDB_MAXNAMELEN` is 65.

XDR records:
- `struct afs_ListAddrByAttributes__xdr` models address lookup attributes by IP, index, or UUID.
- `struct afs_uvldbentry__xdr` models UUID-capable VLDB entries with server UUIDs, uniques, partitions, flags, type volume IDs, clone ID, and spare words.
