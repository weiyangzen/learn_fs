# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_intr_irm.c

## Role

`ddi_intr_irm.c` implements Interrupt Resource Management. IRM manages pools of interrupt vectors, tracks device interrupt requests, balances allocation across devices, and notifies IRM-aware drivers when MSI-X allocations should grow or shrink.

The file defines global IRM enable/active flags, default balancing policy, pool list locking, debug tunables, pool lifecycle routines, request insertion/modification/removal, callback-state changes, the balancing thread, reduction algorithms, and notification helpers.

## Initialization and Pool Lifecycle

`irm_init()` validates the default policy and initializes the global pool list when IRM is enabled. `i_ddi_irm_poststartup()` activates IRM after I/O startup by creating one balancing thread per existing pool and setting `irm_active` so future pools are activated at creation.

`ndi_irm_create()` validates nexus-supplied parameters, allocates a `ddi_irm_pool_t`, records owner, interrupt types, total size, policy, and default size, initializes request and scratch lists plus locks/CV, adds the pool to the global list, and starts a balancing thread if IRM is already active.

`ndi_irm_resize_pool()` updates pool size directly when growing or when current reservations fit the new size. When shrinking below reserved count, it performs a synchronous rebalance and rolls back if the pool cannot free enough vectors.

`ndi_irm_destroy()` requires an empty pool, removes it from the global list, asks the balancing thread to exit if active, joins it, destroys locks/lists/CV, and frees the pool.

## Request Management

`i_ddi_irm_insert()` maps a device into a pool for a given interrupt type. It ignores duplicates, finds a pool through `i_ddi_intr_get_pool()`, detects driver IRM support through `i_ddi_irm_supported()`, computes request/minimum/partial sizes, allocates a `ddi_irm_req_t`, verifies minimum fit, inserts it sorted by request size, and either fulfills directly, partially fulfills plus queues background rebalance, or performs immediate synchronous rebalance. If no interrupt is available at all, it removes the request and returns `DDI_EAGAIN`.

`i_ddi_irm_modify()` changes request size. MSI requests cannot be resized. Increases for non-IRM-aware drivers go through `i_ddi_irm_modify_increase()`, which can use a temporary proxy request for synchronous rebalance while preventing the existing allocation from being reduced. Decreases and IRM-aware changes update pool accounting, resort the request, and queue rebalancing.

`i_ddi_irm_remove()` removes a device request, subtracts minimum/request/reserved counts, queues rebalance, clears `devi_irm_req_p`, and frees the request.

`i_ddi_irm_set_cb()` updates whether a request is callback-capable. Gaining callback support lowers the minimum for MSI-X requests and queues background rebalance. Losing callback support reduces the request to static/default limits, updates minimum accounting, rebalances synchronously before clearing the callback flag, and resorts the request.

`i_ddi_irm_supported()` limits IRM-aware behavior to MSI-X devices with a registered DDI callback carrying `DDI_CB_FLAG_INTR`.

## Balancing Thread and Algorithms

Each pool has an `irm_balance_thread()` that performs initial balancing, marks the pool active, then waits for queued work, timeout intervals, waiters, or exit. Synchronous callers set a waiter flag and sleep on the pool CV until balance completes.

`i_ddi_irm_balance()` resets reducible requests to maximum availability, moves them into a scratch list, calls `i_ddi_irm_reduce()`, and then sends remove notifications before add notifications. If a driver fails to release interrupts after a remove notification, the request is removed from scratch processing, the imbalance is recomputed, and balancing restarts from the head.

`i_ddi_irm_reduce()` computes pool imbalance and first tries policy reduction. If that cannot reduce enough, it reduces a new request as a last resort.

`i_ddi_irm_reduce_by_policy()` supports:
- `DDI_IRM_POLICY_LARGE`, which reduces larger requests first;
- `DDI_IRM_POLICY_EVEN`, which reduces reducible requests evenly.

The algorithm operates on the scratch list sorted by request size, preserves descending order, avoids reducing below the pool default size during policy reductions, and uses batched reductions to minimize iterations.

`i_ddi_irm_reduce_new()` reduces the one new request when policy reductions are insufficient.

## Pool Lookup and Driver Notification

`i_ddi_intr_get_pool()` returns an existing associated pool when compatible, otherwise asks the nexus through `DDI_INTROP_GETPOOL`.

`i_ddi_irm_notify()` compares current availability to the scratch value, determines add/remove action and count, calls the driver's registered callback, logs callback failures, verifies the driver released enough interrupts after remove actions, adjusts pool reserved counts if not, and updates scratch state.

## Locking and Error Behavior

Pool structure is protected by `ipool_lock`; availability reads are isolated by `ipool_navail_lock` because readers can query availability while rebalancing. The global pool list has `irm_pools_lock`. The balancing path is careful about synchronous waiters and avoids deadlock when IRM is not yet active.

Failures are surfaced as `DDI_EINVAL`, `DDI_ENOTSUP`, `DDI_EAGAIN`, or `DDI_FAILURE`, with warnings when pools are too full or drivers fail callbacks/release requirements.

## Subset Relevance

IRM directly affects how many interrupt vectors high-performance storage drivers can allocate. It is important for MSI-X-heavy controllers and therefore part of the storage substrate under subset A.
