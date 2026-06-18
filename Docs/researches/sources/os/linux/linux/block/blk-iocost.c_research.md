# File Research: sources/os/linux/linux/block/blk-iocost.c

## Summary
Implements the cgroup v2 `io.cost` controller, an rq-qos policy that estimates I/O cost in virtual device time and distributes device capacity proportionally across cgroups while adapting to observed latency and queue saturation.

## Main Responsibilities
- Maintain a per-device `struct ioc` rq-qos controller.
- Maintain per-device-cgroup `struct ioc_gq` scheduling state.
- Estimate read/write cost using a linear model with sequential/random and per-page coefficients.
- Throttle bios by virtual-time budget, or account unavoidable bios as debt.
- Dynamically adjust virtual-time rate from request wait and completion-latency signals.
- Donate unused cgroup weight to active cgroups that can use capacity.
- Expose cgroup files `io.weight`, `io.cost.qos`, and `io.cost.model`.

## Key APIs and Hooks
- rq-qos hooks: `ioc_rqos_throttle()`, `ioc_rqos_merge()`, `ioc_rqos_done_bio()`, `ioc_rqos_done()`, `ioc_rqos_queue_depth_changed()`, `ioc_rqos_exit()`.
- Initialization: `blk_iocost_init()`, `ioc_init()`, `ioc_exit()`.
- blkcg policy hooks: `ioc_cpd_alloc()`, `ioc_pd_alloc()`, `ioc_pd_init()`, `ioc_pd_free()`, `ioc_pd_stat()`.
- cgroup operations: `ioc_weight_write()`, `ioc_qos_write()`, `ioc_cost_model_write()`.

## Important Behavior
Each bio receives an absolute cost from the linear model. The cost is scaled by inverse hierarchical in-use weight, so lower-share cgroups consume their local virtual-time budget faster. If the cgroup has enough budget, `iocg_commit_bio()` advances `iocg->vtime` and stores `bio->bi_iocost_cost`; completion advances `done_vtime`.

If a bio is over budget, normal issuers sleep on the cgroup wait queue until enough virtual time is available. Bios that must issue as root or when the task has a fatal signal are charged as `abs_vdebt`; the controller later pays debt from the cgroup’s budget and may induce blkcg delay.

The period timer collects latency/rq-wait stats, deactivates idle groups, wakes oversleeping waiters, updates usage stats, transfers surplus weight, adjusts vrate, refreshes automatic parameters, and forgives debt when the device is sufficiently idle.

## Configuration Model
Automatic presets distinguish HDD, queue-depth-one SSD, default SSD, and fast SSD. Users can override QoS targets and model coefficients. `io.cost.qos` can enable/disable the controller and set latency percentiles and min/max vrate. `io.cost.model` sets linear read/write bandwidth and IOPS coefficients.

## State and Synchronization
Per-device state uses `ioc->lock`, a period timer, seqcount-protected period timestamps, percpu latency counters, active cgroup lists, hweight generations, and atomic virtual-time fields. Per-cgroup state uses wait queues, hrtimers, percpu usage counters, hierarchy ancestor arrays, active/surplus/walk lists, debt/delay fields, and cached hierarchical weights.

## Risks
This file has high concurrency and arithmetic complexity. Correctness depends on synchronized hweight propagation, wait queue locking, debt ownership of `inuse`, timer-driven state transitions, and careful unit conversions between wall time, virtual time, percentages, and ppm. Lazy initialization from cgroup writes means rq-qos hooks must tolerate bios before policy activation is complete.
