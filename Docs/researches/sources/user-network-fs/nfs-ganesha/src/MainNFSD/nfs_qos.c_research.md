# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_qos.c

## Purpose

This file implements the optional NFSv4 QoS engine for NFS-Ganesha. It applies configured bandwidth, token, IOPS, and data-server controls to NFS read/write and compound paths, suspends work that exceeds configured limits, and resumes deferred work from dedicated QoS threads. It supports per-export, per-client, and per-export-per-client policy modes.

The file is guarded by the `ENABLE_QOS` build path through `nfs_qos.h` and integrates with NFSv4 read/write callbacks (`nfs4_qos_read_cb`, `nfs4_qos_write_cb`, `nfs4_qos_compound_cb`), export/client lifetime hooks, global runtime config, TI-RPC socket suspension/resumption, and optional monitoring gauges.

## Important APIs, types, and functions

The exported entry points are `qos_init`, `shutdown_qos`, `qos_process`, `qos_process_iops`, `qos_perexport_insert`, `qos_free_mem`, `qos_drain_bw_ios`, `qos_drain_iops_ios`, `copy_gsh_qos_conf`, and `pepc_get_client_from_list`. They are the public lifecycle, request gating, config insertion, cleanup, and config-copy interfaces.

Core state comes from `nfs_qos.h`: `qos_block_config_t` stores global/per-export configuration; `qos_class_t` represents an export or client QoS class; `qos_bucket_t` stores read/write accounting and wait queues; `timer_entry_t` stores delayed callbacks; `qos_client_entry_t` groups token-exhausted I/O by client and transport; `qos_status_t`, `qos_class_type_t`, and `qos_op_type_t` describe suspension status, class kind, and read/write operation kind.

Global state includes `qos_block_config`, `g_qos_config`, `qos_bits`, `g_qos_iopath_lock`, `g_qos_config_lock`, and two `qos_thread` workers. `QOS_THREAD_RUNNABLE` controls worker lifecycle. The locking comment near the globals is important: config updates use `g_qos_config_lock`, IO-path lazy creation also uses `g_qos_iopath_lock`, producers manipulate bucket queues with `bucket->lock`, and PEPC consumer paths can hold export and client bucket locks while moving entries between queues.

Allocation and list helpers include `allocate_qos_class`, `allocate_client`, `alloc_clientdetails_pe`, `alloc_qos_cb_args`, `create_timer_entry`, `insert_timer_entry_sorted`, `insert_timer_entry`, `resume_timer_entry`, `release_wait_ios`, and `execute_qos_expired_timers`. `get_qos_resume_func` maps `QOS_READ`/`QOS_WRITE` to the appropriate NFSv4 resume callback; `qos_cb_str` is debug-only callback labeling.

Config application is centered on `set_class_values`, `update_class_token_values`, `update_class_bw_values`, `update_class_ds_values`, `update_class_iops_values`, `setNode_pe`, and `setNode_pc`. These copy numeric limits into read/write buckets, choose combined read/write mode by using the write bucket as the combined bucket, drain queues when features are disabled or switched, and optionally register metrics through `register_qos_metrics`.

Request processing is split by policy: `qos_process_pe`, `qos_process_pc`, and `qos_process_pepc` feed `qos_check_pe_pc` or `qos_check_pepc` for token and bandwidth decisions. IOPS processing is similarly split through `qos_process_iops_pe`, `qos_process_iops_pc`, and `qos_process_iops_pepc`, with `qos_iops_check` and `qos_iops_suspend_task` doing the bucket accounting.

The consumer side is handled by `qos_thread_func`, `resume_io`, `refresh_qos_token`, `resume_bw_io`, `resume_bw_io_pepc`, `pepc_reschedule_bw_io`, `resume_ops_io`, `resume_iops_pepc`, and `pepc_reschedule_iops`. Iterator callbacks (`ps_io_control_iter`, `pc_io_control_iter`, `pepc_io_control_iter`, `ps_token_control_iter`, `pc_token_control_iter`, `pepc_token_control_iter`) traverse the global export/client registries.

## Control flow

Startup calls `qos_init`, which initializes the two global mutexes and calls `qos_thread_init` if QoS is enabled. `qos_thread_init` sets `QOS_THREAD_RUNNABLE` and creates one read worker and one write worker. Each worker loops while the flag is set, calls `resume_io(op_type)` to release expired BW/IOPS work, and the write worker periodically calls `refresh_qos_token` every `TOKEN_REFRESH_DELAY` loop iterations.

On the producer path, NFS read/write code calls `qos_process(size, caller_data, data, op_type, is_ds)`. The function returns immediately if QoS is globally disabled or data-server control is not enabled for DS operations. It dispatches by `g_qos_config->qos_type`: per-export lazily creates `op_ctx->ctx_export->qos_class`; per-client lazily creates `op_ctx->client->qos_class`; PEPC lazily creates the export class and then per-client sub-classes in the export's `clients` list.

For per-export and per-client, `qos_check_pe_pc` takes the class lock, checks token availability, potentially enqueues token-exhausted work, consumes tokens, and then applies bandwidth control. For PEPC, `qos_check_pepc` finds or creates the sub-client class, checks export and client token limits, consumes both, and if client bandwidth control is enabled queues the operation into the client bucket for later rescheduling to the export bucket.

Token exhaustion uses `qos_token_exausted_suspend_task`. It creates a callback arg with `NON_RATELIMITING_IO`, calculates a wakeup time bounded by token refresh time and `TOKEN_NFS_ERR_DELAY_DEFAULT`, groups waits under a `qos_client_entry_t`, and after `SUSPEND_SOCKET_IO_LIMIT` pending operations suspends socket receive with `svc_rqst_qos_suspend_socket`. `refresh_qos_client` later releases expired or token-refresh-unblocked operations and calls `svc_rqst_qos_resume_socket` when the client entry drains.

Bandwidth control uses a virtual last-departure timestamp (`bw_ldct`) and `required_time = bytes * 1000000 / max_bw_allowed`. If the computed schedule is in the future, `qos_process_bw` queues a timer entry; otherwise it accounts consumption and lets the operation continue. PEPC bandwidth first queues to client buckets, then `pepc_reschedule_bw_io` moves eligible entries into export buckets sorted by expiry, and `resume_bw_io_pepc` releases export-bucket entries subject to export-level pacing.

IOPS control uses compound operation count (`data->argarray_len`) rather than byte count. `qos_iops_check` sets `IS_QOS_IOPS_ACCOUNTED`, advances `iops_ldct`, and either accounts immediately or queues a compound callback. PEPC IOPS enqueues at the client bucket immediately; the QoS thread later reschedules to the export bucket and resumes entries.

Shutdown calls `shutdown_qos`. It clears the runnable bit under `g_qos_iopath_lock`, disables `g_qos_config->enable_qos`, joins both worker threads, drains all pending QoS I/O through `stop_qos_io`, and destroys the global mutexes.

## State and persistence behavior

The QoS state is runtime-only and attached to live `gsh_export` and `gsh_client` objects. Per-export config may allocate `gsh_export->qos_block` and `gsh_export->qos_class`; per-client config uses `gsh_client->qos_class`; PEPC stores per-client `qos_class_t` instances in an export class `clients` list. There is no on-disk persistence in this file.

Each bucket persists rate-control accounting across operations: `bw_ldct`, `data_consumed`, `iops_ldct`, `iops_consumed`, `token_ldct`, `tokens_consumed`, maximum limits, metric handles, and wait-list length. Token buckets reset `tokens_consumed` only when the consumed amount is at or over the limit and the renew time has elapsed.

Timer entries own callback arguments allocated by `alloc_qos_cb_args`; `resume_timer_entry` calls the stored callback, unlinks the timer, and frees only the timer entry. The resume callback is therefore responsible for finishing or freeing its argument chain. Token-exhausted client entries are freed when their wait list drains.

Runtime config update paths can drain queues and mutate class flags. `copy_gsh_qos_conf` propagates export QoS config during export copy/reexport flows and re-applies PEPC client node values under the export class lock. Runtime enablement is partially supported by lazy class creation, while the comment near `qos_init` says full runtime enable/disable is not supported except through a separate thread-init path.

## Dependencies and integration points

The file depends on NFS-Ganesha core context (`op_ctx`, `compound_data_t`, `gsh_export`, `gsh_client`, export/client iterators), NFSv4 callback hooks, the Ganesha list and memory APIs, pthreads and atomics, monotonic time, TI-RPC request transport functions, and optional monitoring (`nfs_metrics.h`, `monitoring__register_gauge`, `monitoring__gauge_set`, `sprint_sockip`).

It integrates with export/client lifetime through `qos_free_mem`, `pe_stop_iter`, and `pc_stop_iter`; with export reconfiguration through `qos_perexport_insert`, `qos_perclientinsert`, and `copy_gsh_qos_conf`; with the request path through `qos_process` and `qos_process_iops`; and with shutdown through `shutdown_qos`.

The monitoring integration labels metrics by export path, client address, or export-client pair. Metrics are registered lazily when the class feature is enabled and reset when queues are drained or tokens refresh.

## Risks and edge cases

There are several subtle arithmetic and synchronization risks. Bandwidth and IOPS scheduling divide by configured maxima, so validation must guarantee nonzero values. Combined read/write mode redirects to the write bucket; switch-over paths must drain the correct queues or read-bucket entries can remain stuck. In `update_class_bw_values`, the combined-mode branch checks `wbucket->io_waitlist_qos_bc` but releases `rbucket->io_waitlist_qos_bc`, which looks suspicious and should be tested carefully.

PEPC locking is delicate. `qos_check_pepc` checks token availability on the sub-client before taking the export class lock and does not lock the sub-client class around all token operations. The design comment says export-level locking protects runtime disablement while bucket locks protect consumer manipulation, but PEPC token and class list interactions are a high-risk concurrency area.

Token availability uses `tokens_consumed <= max_available_tokens`, not `tokens_consumed + rsize <= max_available_tokens`. This allows an operation that crosses the limit to pass and only blocks later operations. That may be intentional burst semantics, but tests should encode it.

`qos_get_time_to_tokenrefresh` assumes a non-NULL token bucket; callers only use it after token checks, but malformed state could dereference NULL. `release_wait_ios` and `execute_qos_expired_timers` decrement both counters blindly, and some callers pass dummy counters initialized to `UINT32_MAX`, which is safe only because the dummy is intentionally ignored.

The shutdown path disables global QoS and joins threads before draining queues. Any producer still entering the QoS path during shutdown could interact with destroyed mutexes if lifecycle ordering is wrong. The socket-suspend path also stores `SVCXPRT *` in token client entries and later resumes it after freeing the entry, so transport lifetime assumptions matter.

## Test signals

Useful signals are unit or integration tests that exercise `qos_process` return values, token exhaustion and refresh, bandwidth/IOPS queueing and release, combined read/write mode, PE/PC/PEPC lazy class creation, data-server bypass behavior, export/client cleanup, shutdown draining, and socket suspend/resume thresholds.

Runtime tests should inspect that delayed callbacks are eventually invoked, counters return to zero after drain, no operation stays queued after disabling a QoS feature, and PEPC client queues are rescheduled to export queues in sorted expiry order. Monitoring builds should verify gauges are registered once per class/bucket and reset on drain or token refresh. Stress tests should include concurrent request producers, runtime export config updates, and export/client destruction while queues contain entries.
