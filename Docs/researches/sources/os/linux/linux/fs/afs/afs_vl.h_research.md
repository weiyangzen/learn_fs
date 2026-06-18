# File Research: sources/os/linux/linux/fs/afs/afs_vl.h

Purpose: defines AFS Volume Location service constants, operations, errors, VLDB entry layout, and XDR request/response structures.

Key contents:
- `AFS_VL_PORT = 7003`, `VL_SERVICE = 52`, `YFS_VL_SERVICE = 2503`.
- VL/YFS operation IDs for entry lookup, probes, address lookup, endpoints, cell name, and capabilities.
- VL error code enum.
- YFS server/endpoint indexes and endpoint family tags.
- `struct afs_vldbentry`: volume name, type, server count, clone ID, flags, volume IDs, and server records.
- XDR structs for ListAddrByAttributes and UUID VLDB entries.

Implementation notes:
- Supports both classic AFS VL and UUID/YFS-extended server addressing.
- Flags identify read-write/read-only/backup volume presence and per-server volume placement.
