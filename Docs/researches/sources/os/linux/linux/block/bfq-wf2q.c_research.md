# File Research: sources/os/linux/linux/block/bfq-wf2q.c

`bfq-wf2q.c` implements BFQ’s hierarchical Budget Worst-case Fair Weighted Fair Queueing engine. It schedules generic `bfq_entity` objects, which may be leaf queues or cgroup/group entities, across per-priority-class service trees.

Timestamp and tree foundation:
- `bfq_gt()` compares virtual timestamps with wraparound handling.
- `WFQ_SERVICE_SHIFT` controls fixed-point virtual-time precision.
- `bfq_delta()` converts service to virtual time using weight.
- `bfq_calc_finish()` computes entity finish timestamps from start, service/budget, and weight.
- Active and idle entities are stored in rbtree structures ordered by finish time.
- Active tree nodes also maintain `min_start` for efficient eligibility lookup.
- Helpers insert/extract active and idle entities, update active-tree min-start state, and track first/last idle entries.
- `bfq_forget_idle()` advances virtual time and removes expired idle entities to bound idle-tree growth.

Entity weights and priority:
- `bfq_ioprio_to_weight()` maps I/O priority to BFQ weight.
- `__bfq_entity_update_weight_prio()` lazily applies weight/ioprio/ioprio-class changes, handles cgroup weight changes, updates service-tree weight sums, adjusts queue weight counters, and preserves class-tree consistency.

Activation and requeue:
- `__bfq_activate_entity()` activates a previously inactive entity, possibly extracting it from idle, assigning start time, adding service reference, and inserting it into active tree.
- `bfq_update_fin_time_enqueue()` recalculates finish time and handles backshifted timestamps for non-blocking wait reactivations.
- `__bfq_requeue_entity()` repositions in-service or active entities after service/budget changes.
- `bfq_activate_requeue_entity()` propagates activation/requeue up the hierarchy and updates cached `next_in_service`.
- Wrappers `bfq_activate_bfqq()` and `bfq_requeue_bfqq()` apply this to leaf queues.

Deactivation:
- `__bfq_deactivate_entity()` removes an entity from active/idle/in-service state, optionally inserting it into idle tree if finish time is still in the future.
- `bfq_deactivate_entity()` propagates deactivation up the hierarchy, then requeues/repositions ancestors whose child `next_in_service` changed.
- `bfq_deactivate_bfqq()` applies this to a leaf queue.

Service accounting:
- `bfq_bfqq_served()` charges actual served sectors to the queue and all ancestors, updates service counters, virtual time, idle cleanup, weight-raising service, and backlogged service.
- `bfq_bfqq_charge_time()` converts elapsed service time into an equivalent service amount for slow queues, preserving time fairness when throughput fairness would hurt performance.

Candidate selection:
- `bfq_update_next_in_service()` maintains each sched_data’s cached next entity, often avoiding full lookup when only one entity changed.
- `bfq_calc_vtime_jump()` and `bfq_update_vtime()` ensure at least one entity is eligible.
- `bfq_first_active_entity()` finds the eligible active entity with smallest finish time in O(log N) using `min_start`.
- `bfq_lookup_next_entity()` chooses among priority classes, occasionally serving idle class to guarantee minimum bandwidth and reduce priority inversion.
- `next_queue_may_preempt()` reports whether cached next differs from current in-service entity.
- `bfq_get_next_queue()` walks from root sched_data to a leaf queue, sets each entity along the path in service, extracts no-longer-candidate entities, then updates next-service caches upward.

In-service reset and busy accounting:
- `__bfq_bfqd_reset_in_service()` clears wait state, cancels idle timer, resets in-service entity pointers along the hierarchy, and drops service refs if appropriate.
- `bfq_add_bfqq_busy()` activates a queue, marks it busy, updates busy counts, pending-group counts, weight counters, weight-raised counts, and waker-list ordering.
- `bfq_del_bfqq_busy()` clears busy state, decrements counts, updates dequeue stats, deactivates the queue, removes pending-group state and weight counters when no dispatched requests remain.
- `bfq_add_bfqq_in_groups_with_pending_reqs()` and `bfq_del_bfqq_in_groups_with_pending_reqs()` maintain group-level pending-request counts under group scheduling.

Group scheduling conditionals:
- With `CONFIG_BFQ_GROUP_IOSCHED`, parent budgets and active entity counts are maintained, and non-leaf entities can remain next-service candidates if they have multiple active children.
- Without group scheduling, parent budget updates and active entity count hooks are no-ops.

The file is the core fairness engine behind BFQ’s service guarantees and latency/throughput behavior.
