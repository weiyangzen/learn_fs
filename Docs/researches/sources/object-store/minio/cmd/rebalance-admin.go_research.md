# sources/object-store/minio/cmd/rebalance-admin.go

## Purpose
This file builds admin-facing rebalance status for erasure server pools.

## Important APIs, Types, and Functions
`rebalPoolProgress` reports object/version counts, bytes, bucket/object markers, elapsed time, and ETA. `rebalancePoolStatus` reports pool id, status, used fraction, and progress. `rebalanceAdminStatus` is the top-level status returned to admin clients. `rebalanceStatus` loads rebalance metadata, computes per-pool disk usage from `StorageInfo`, and fills progress/ETA for participating pools.

## Control Flow and State
The function loads persisted `rebalanceMeta` from pool 0, then derives current disk usage by summing disk available/total space per pool. ETA is estimated from target bytes, elapsed time, and bytes already processed, and is zeroed when the pool stopped or completed.

## Dependencies and Integration Points
The file depends on erasure pool metadata, storage info, rebalancing status enums, and admin serialization tags.

## Risks and Test Signals
`Used` can divide by zero if a pool reports zero total space. ETA can be unstable early in a rebalance, especially if `ps.Bytes` is zero. No direct tests in this subset; admin rebalance tests should verify stopped/completed/active cases.
