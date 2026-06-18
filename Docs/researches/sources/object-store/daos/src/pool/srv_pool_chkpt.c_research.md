# sources/object-store/daos/src/pool/srv_pool_chkpt.c

## Purpose
`srv_pool_chkpt.c` owns the per-pool-target checkpoint ULT that drives VOS checkpointing for pools whose storage backend needs explicit checkpoints. It converts pool checkpoint properties and WAL usage notifications into periodic or threshold-based calls to `vos_pool_checkpoint`.

## Important APIs, types, and functions
The public API is `ds_start_chkpt_ult(struct ds_pool_child *child)` and `ds_stop_chkpt_ult(struct ds_pool_child *child)`. The central state is `struct chkpt_ctx`, which tracks the pool child, VOS handle, backing `umem_store`, current committed WAL ID, WAL wait ID, checkpoint thresholds, current/total used blocks, scheduler request, and an Argobots eventual. VOS callbacks are `update_cb` and `wait_cb`; scheduling helpers are `yield_fn`, `wait_fn`, `wake_fn`, and `need_checkpoint`.

## Control flow
`ds_start_chkpt_ult` starts only when `vos_pool_needs_checkpoint(child->spc_hdl)` is true. It creates a scheduler request with GC priority and deep stack, then launches `chkpt_ult`. The ULT initializes an ABT eventual, fills `chkpt_ctx`, and calls `vos_pool_checkpoint_init` with update and wait callbacks. Its loop calls `need_checkpoint`: disabled mode only sleeps, lazy mode checkpoints only on WAL block threshold, and timed mode checkpoints when either the threshold is crossed or the configured frequency elapses. When checkpointing is needed, it calls `vos_pool_checkpoint`, handles shutdown specially, logs other errors, and restarts the timer.

`wait_cb` is invoked by VOS when checkpointing must wait for WAL commitment. If the requested checkpoint transaction is already committed it yields to make scheduler progress, otherwise it records `cc_wait_id` and blocks on the eventual unless the store is faulty. `update_cb` records WAL usage and committed ID, wakes a sleeping ULT when block usage crosses threshold, and wakes a waiting checkpoint when the committed ID catches up or the store becomes faulty.

## State and persistence behavior
The persistent behavior is VOS pool checkpoint creation over WAL-backed storage. The ULT keeps only volatile scheduling state but reacts to persistent WAL usage counts and pool properties. Checkpoint parameters are read from `struct ds_pool`: `sp_checkpoint_mode`, `sp_checkpoint_freq`, and `sp_checkpoint_thresh`; threshold changes recalculate `cc_max_used_blocks`. `vos_pool_checkpoint_fini` unregisters callbacks before the eventual is freed.

## Dependencies and integration points
This file is started from pool-child startup in `srv_target.c` after VOS pool open and stopped during pool-child shutdown. It depends on scheduler request sleep/wakeup/yield, Argobots event synchronization, the VOS checkpoint API, `umem_store` WAL ID comparison, and pool property propagation. `ds_pool_tgt_prop_update` wakes this ULT when checkpoint properties change.

## Risks and test signals
Risks include missed wakeups between VOS callbacks and scheduler sleep, incorrect threshold recalculation when total blocks change, blocking forever if faulty-store or WAL ID updates are mishandled, and excessive checkpoint frequency under timed mode. Useful tests should vary checkpoint mode/frequency/threshold at runtime, simulate WAL usage crossing thresholds, verify shutdown unblocks waits, and confirm `vos_pool_checkpoint_fini` runs even after checkpoint errors.
