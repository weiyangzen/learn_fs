# sources/user-network-fs/samba/source4/dsdb/repl/drepl_ridalloc.c

Purpose: detects low local RID pool state and requests a new pool from the RID Manager FSMO owner using DRS extended operation `DRSUAPI_EXOP_FSMO_RID_ALLOC`.

Important APIs/functions: `dreplsrv_ridalloc_check_rid_pool()` is the service check; `drepl_ridalloc_pool_exhausted()` inspects this DC's RID Set; `drepl_request_new_rid_pool()` schedules the extended op; `drepl_new_rid_pool_callback()` clears `rid_alloc_in_progress`; `dreplsrv_allocate_rid()` is the messaging hook triggered by samldb.

Control flow/state: RODCs and in-progress allocations return immediately. The check finds the RID Manager object, reads `fSMORoleOwner`, skips if this DC is the RID master, then treats no local RID Set or the second half of the previous allocation pool as needing a new pool. On scheduling success, `service->rid_alloc_in_progress` prevents duplicate requests until callback completion. Persistent RID changes are produced by remote FSMO behavior and replication, not direct writes here.

Dependencies/integration: SAMDB RID/FSMO helpers, DREPL extended operation scheduler, messaging `MSG_DREPL_ALLOCATE_RID`, and RID Set attributes (`rIDAllocationPool`, `rIDPreviousAllocationPool`, `rIDNextRid`). Risks include threshold assumptions, no direct caller status from the messaging hook, and stuck in-progress state if callbacks are lost. Test signals: RODC skip, RID-master skip, no-RID-set bootstrap request, half-pool threshold, and duplicate suppression while an exop is pending.
