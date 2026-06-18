# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RatekeeperLimitReasons.h

## Purpose
This header enumerates the reason codes ratekeeper uses when selecting a transaction rate limit.

## Important APIs, Types, And Functions
`limitReason_t` includes `unlimited`, storage-server queue/write/readable/free-space/durability reasons, log-server MVCC/queue/free-space reasons, storage-server list fetch failure, and `limitReason_t_end`. External arrays `limitReasonName` and `limitReasonDesc` map codes to readable diagnostics; `limitReasonEnd` mirrors the enum end.

## Control Flow
Ratekeeper code computes limiting metrics, chooses a reason, and uses the name/description arrays for trace or status output.

## State And Persistence Behavior
There is no mutable or persistent state in the header. The enum values are diagnostic contract state and should remain stable for logs/status consumers.

## Dependencies And Integration Points
It is standalone and integrates with ratekeeper tracing, status JSON, metrics, and operator diagnostics.

## Risks And Edge Cases
Adding enum values requires updating the external arrays in lockstep. Reordering can break dashboards or tooling that interpret numeric reason codes.

## Test Signals
Tests or static checks should ensure `limitReasonEnd` and the name/description arrays match `limitReason_t_end`, and that ratekeeper emits expected reasons under synthetic bottlenecks.
