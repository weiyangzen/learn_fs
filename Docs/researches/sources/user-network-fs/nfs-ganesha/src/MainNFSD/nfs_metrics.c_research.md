<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_metrics.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_metrics.c

## Purpose
Registers and updates built-in monitoring metrics for Ganesha: build info, RPC counts/gauge, NFSv4 operation latency/count by opcode/status, compound metrics, dropped GSS requests, and dynamic NFSv3/NFSv4 request observations.

## Important APIs, Types, And Functions
- `FOREACH_NFS_STAT4`, `enum nfsstat4_index`, `nfsstat4_to_index()`, and `index_to_nfsstat4[]` map protocol statuses to dense metric indexes.
- `register_ganesha_info_metrics()` registers `ganesha_build_info`.
- `nfs_metrics__init()` registers core metric handles.
- `nfs_metrics__nfs4_op_completed()`, `nfs_metrics__nfs4_compound_completed()`, RPC update functions, and GSS drop update functions observe/increment metrics.
- `nfs_metrics__nfs3_request()` and `nfs_metrics__nfs4_request()` feed dynamic metrics.

## Control Flow
Initialization registers counters/gauges/histograms. NFSv4 operation registration eagerly creates metric handles for every opcode/status pair. Runtime request paths call update helpers, converting nanosecond latency to milliseconds.

## State And Persistence Behavior
State is static metric handles and monitoring registry entries. Export/persistence is handled by the monitoring backend.

## Dependencies And Integration Points
Depends on monitoring, dynamic metrics, NFS status/op conversion helpers, and protocol constants. Called from `nfs_init.c`.

## Risks
- Eager opcode/status registration can create high metric cardinality.
- Update functions assume initialization has run.
- Unknown NFSv4 status maps to a synthetic unknown bucket.
- Dynamic labels such as path and client IP can be high cardinality.

## Test Signals
Test registration, known/unknown status mapping, latency conversion, NFSv3 conditional path, dynamic metrics cardinality, and update-before-init protection at call sites.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_metrics.c -->
