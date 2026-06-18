# sources/user-network-fs/nfs-ganesha/src/include/sal_metrics.h

## Purpose
This header declares monitoring hooks for SAL-level client, lease, lock, session, and transport/session association metrics.

## Important APIs, Types, And Control Flow
It defines `sal_metrics__lock_type` with holders, waiters, and count values. Functions record confirmed client totals, lease expiration events, client state-protection type, lock increments/decrements, session connection distributions, denied xprt/session associations, xprt custom data status, xprt session counts, and `sal_metrics__init`.

## State And Persistence
State is owned by the monitoring subsystem initialized by `sal_metrics__init`. The header itself has no storage. Metrics are runtime observability data and may be exported to the configured monitoring backend.

## Dependencies And Integration Points
It includes `monitoring.h`, `nfsv41.h`, and `xprt_handler.h`. It integrates SAL state changes, session connection tracking, and transport custom-data lifecycle with monitoring counters/histograms.

## Risks And Test Signals
Metrics must not perturb SAL locking or allocate in hot paths unexpectedly. Tests should verify init idempotence, enum label coverage, increments/decrements balancing, transport status labels, and that metrics calls remain safe when monitoring is disabled.
