# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiCluster.hh

## Purpose
Defines the server-cluster management interface passed to SSI server providers so they can report endpoint names, service availability, resource capacity, managers, and utilization.

## Important APIs, Types, And Functions
- `Added(name, pend)` and `Removed(name)` publish logical resource availability.
- `DataContext()` distinguishes data-server context from metadata-manager context.
- `Managers(int &mNum)` returns the permanent manager-node list.
- `Suspend(perm)` and `Resume(perm)` control service availability.
- `Resource(n)`, `Reserve(n)`, and `Release(n)` manage resource units and dispatch suspension/resume.
- `Utilization(util, alert)` reports server utilization to managers.

## Control Flow
Implementations track cluster-visible names and resource levels. Reserving resources can temporarily suspend dispatch when capacity becomes non-positive; releasing resources can resume dispatch when capacity becomes positive. Utilization reports may be throttled unless `alert` is true.

## State And Persistence
This header defines no state, but implementations are expected to persist permanent suspend/resume decisions across server restarts when `perm` is true and to maintain current resource counters and advertised names during runtime.

## Dependencies And Integration Points
Pure abstract interface with no includes. It is consumed by SSI server/provider startup and lets application-level SSI services interact with XRootD clustering and manager selection.

## Risks And Edge Cases
Resource accounting must be thread-safe in implementations. Permanent versus temporary suspend semantics must be clear to avoid unintentionally draining a server after restart. Manager-list lifetime is specified as permanent and must not be freed by callers.

## Test Signals
Implementation tests should verify added/removed name propagation, data/meta context reporting, permanent manager-list lifetime, suspend/resume persistence flags, resource counter bounds, reserve/release transitions around zero, and utilization alert throttling.
