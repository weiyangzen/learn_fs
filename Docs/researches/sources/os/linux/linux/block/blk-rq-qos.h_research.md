# File Research: sources/os/linux/linux/block/blk-rq-qos.h

Purpose: Header defining request QoS IDs, structures, operations, and inline invocation helpers.

Key contents:
- Defines QoS IDs: writeback throttling, latency, and cost.
- Defines `rq_wait`, `rq_qos`, `rq_qos_ops`, and `rq_depth`.
- Provides lookup helpers `rq_qos_id()`, `wbt_rq_qos()`, and `iolat_rq_qos()`.
- Declares QoS add/delete, wait, depth scaling, and callback-chain functions.
- Provides inline fast-path guards checking `QUEUE_FLAG_QOS_ENABLED` and `q->rq_qos`.
- Marks bios with `BIO_QOS_THROTTLED` and `BIO_QOS_MERGED` so bio completion can notify QoS modules.

Concurrency and lifecycle notes:
- `rq_qos_done_bio()` defensively rechecks queue QoS state because stacked devices may propagate BIO_QOS flags across queues where the top queue has no QoS module.
- Inline request-done skips passthrough requests.

Dependencies:
- Public block, bio, atomic, waitqueue headers.
- Debugfs attribute declarations.

Filesystem/block relevance:
- Defines the extension contract for block-layer QoS controllers affecting filesystem I/O latency and throughput.
