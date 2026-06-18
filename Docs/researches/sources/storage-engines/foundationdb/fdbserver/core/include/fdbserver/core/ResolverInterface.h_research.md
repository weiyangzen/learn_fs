# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ResolverInterface.h

## Purpose
This header defines the resolver role RPC interface and conflict-resolution request/reply payloads used by commit proxies.

## Important APIs, Types, And Functions
`ResolverInterface` exposes `resolve`, `metrics`, `split`, `waitFailure`, and `txnState`, with locality and unique ID. `ResolveTransactionBatchRequest` carries span context, version window, transactions, transaction-state transaction offsets, written tags, and last shard move. `ResolveTransactionBatchReply` returns per-transaction commit flags, state mutations, conflicting read ranges, private mutations by TLog location, two-phase commit version map, written tags, and last shard move. Metrics and split APIs are `ResolutionMetricsRequest/Reply` and `ResolutionSplitRequest/Reply`.

## Control Flow
Commit proxies send batches to resolvers for conflict checking. Resolvers reply with commit/abort decisions and private mutation payloads. Metrics and split requests support load and shard-boundary decisions.

## State And Persistence Behavior
Requests are transient, but resolver state tracks key conflict ranges and system transaction mutations across versions. Replies feed durable TLog commits.

## Dependencies And Integration Points
It depends on commit proxy interfaces, commit transaction structures, timed requests, locality, and RPC. It integrates with commit proxies, master recovery transaction-state broadcasts, data movement, and DD split logic.

## Risks And Edge Cases
Version ordering, arena lifetime, private mutation counts, conflicting range IDs, and two-phase commit maps are correctness-critical. Resolver endpoint load-balance flags affect routing freshness.

## Test Signals
Signals include conflict checking correctness, committed vector size matching input transactions, private mutation serialization, split-key metrics, transaction-state replay, and resolver failure/recruitment behavior.
