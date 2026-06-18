# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RatekeeperInterface.h

## Purpose
This header defines the RPC interface for the ratekeeper role, which supplies transaction rate limits, health metrics, client tag throttles, commit-cost estimates, and storage-server version lag.

## Important APIs, Types, And Functions
`RatekeeperInterface` exposes `waitFailure`, `getRateInfo`, `haltRatekeeper`, `reportCommitCostEstimation`, and `getSSVersionLag`. `TransactionCommitCostEstimation` aggregates operation and cost sums. `GetRateInfoRequest/Reply` exchange released transaction counts, throttled tag counts, detail level, transaction/batch rates, lease duration, health metrics, and optional client throttles. Other messages include `HaltRatekeeperRequest`, `ReportCommitCostEstimationRequest`, and `GetSSVersionLagRequest/Reply`.

## Control Flow
GRV proxies periodically ask for rate info, report how many transactions were released, and receive a lease-backed limit. Storage/commit paths can report tag commit-cost estimates. Cluster controller can halt or wait on the role.

## State And Persistence Behavior
The interface is transient. The data reflects in-memory ratekeeper calculations and health metrics, not persisted state, although throttling decisions influence committed workload throughput.

## Dependencies And Integration Points
It depends on commit proxy types, health metrics, transaction tags, RPC streams, locality, and FDB types. It integrates with GRV proxies, storage servers, commit-cost estimation, and cluster controller recruitment.

## Risks And Edge Cases
Stale rate leases, missing detailed metrics, huge tag maps, or incorrect cost aggregation can over-throttle or under-throttle clients. `TransactionCommitCostEstimation` must remain consistent with `UpdateCommitCostRequest`.

## Test Signals
Tests should validate rate reply serialization, tag throttle propagation, cost aggregation, ratekeeper failure handling, and primary/remote storage-server lag reporting.
