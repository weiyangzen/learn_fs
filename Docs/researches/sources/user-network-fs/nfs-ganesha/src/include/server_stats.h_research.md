# sources/user-network-fs/nfs-ganesha/src/include/server_stats.h

## Purpose
This public statistics header declares hooks used by request-processing paths to update server, operation, IO, transport, and delegation statistics.

## Important APIs, Types, And Control Flow
It declares `server_stats_nfs_done`, optional `server_stats_9p_done`, `server_stats_io_done`, `server_stats_compound_done`, `server_stats_nfsv4_op_done`, `server_stats_transport_done`, and delegation counters `inc_grants`, `dec_grants`, `inc_revokes`, `inc_recalls`, and `inc_failed_recalls`.

## State And Persistence
The functions update in-memory per-server, per-client, per-export, and protocol-specific statistic structures. Persistence is observability output through DBus/monitoring or log reporting, not this header.

## Dependencies And Integration Points
It references `nfs_request_t`, `gsh_client`, optional 9P request data, and NFS operation/status timing. Protocol dispatchers and FSAL IO paths call these hooks after work completes.

## Risks And Test Signals
Stats hooks run on request hot paths, so locking, null clients, and overflow behavior matter. Tests should cover successful/failed IO, duplicate NFS requests, compound status reporting, per-operation latency, transport byte counters, and delegation grant/recall/revoke accounting.
