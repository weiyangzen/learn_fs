# sources/user-network-fs/nfs-ganesha/src/include/sal_functions.h

## Purpose
This header declares the operational API for the State Abstraction Layer: state/error conversion, owner/client/session/stateid management, locks, delegations, layouts, shares, async work, and recovery backends.

## Important APIs, Types, And Control Flow
It exports state error formatting/conversion, owner refcount/display/get/free APIs, `STATELOCK_lock`/`STATELOCK_unlock`, `state_hdl_init`/cleanup, optional 9P and NLM owner/state helpers, NFSv4 client-id lifecycle functions, session table operations, stateid validation and update helpers, state refcount helpers, lease update/reservation, NFSv4 owner seqid replay support, lock test/lock/unlock/cancel/grant APIs, state add/set/delete and safe reference getters, delegation grant/recall/revoke/CB_GETATTR helpers, layout segment operations, NLM share APIs, async scheduling/upcalls/polling, grace/recovery APIs, and `struct nfs4_recovery_backend` function table.

## State And Persistence
The APIs mutate the global SAL data declared in `sal_data.h`: hashes, lists, pools, refcounts, state object lists, lock lists, session connection lists, grace status, and recovery metadata. Persistent state is handled through recovery backends, client stable storage, RADOS or filesystem grace tracking, and FSAL lock/delegation state.

## Dependencies And Integration Points
It depends on `sal_data.h`, `fsal.h`, `gsh_recovery.h`, LTTng traces, and protocol structures. It is the primary contract between NFS protocol handlers, FSAL implementations, recovery modules, statistics/metrics code, and transport/session management.

## Risks And Test Signals
The biggest risks are deadlocks, refcount leaks/use-after-free, replay-cache mistakes for NFSv4.0 seqids, stale stateid handling, lock grant races, and grace-period membership errors. Test signals include NFSv4.0 replay and lease tests, NFSv4.1 session slot reuse, stateid special cases, lock conflict/blocked/async grant flows, delegation recall/revoke, layout return/recall, client restart/reclaim, and recovery backend failover tests.
