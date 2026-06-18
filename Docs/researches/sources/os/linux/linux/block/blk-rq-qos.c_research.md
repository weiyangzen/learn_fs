# File Research: sources/os/linux/linux/block/blk-rq-qos.c

Purpose: Implements the request-queue QoS framework used by writeback throttling, latency control, and cost-based controllers.

Key responsibilities:
- Provides callback-chain dispatch for cleanup, done, issue, requeue, throttle, track, merge, done_bio, and queue-depth-changed events.
- Provides atomic inflight accounting helper `rq_wait_inc_below()`.
- Implements scalable depth adjustment through `rq_depth_calc_max_depth()`, `rq_depth_scale_up()`, and `rq_depth_scale_down()`.
- Implements `rq_qos_wait()` for sleeping until inflight budget is available.
- Adds/removes QoS modules under `q->rq_qos_mutex` with queue freeze protection.
- Exits all QoS modules and clears `QUEUE_FLAG_QOS_ENABLED`.

Concurrency and lifecycle notes:
- Wait wakeup path deliberately acquires budget in the wake function and removes wait entries carefully to avoid use-after-free.
- `rq_qos_add()` and `rq_qos_del()` freeze the blk-mq queue because no I/O may be in flight while changing the chain.
- Callback traversal follows the singly linked `q->rq_qos` chain.

Dependencies:
- `blk-rq-qos.h`.
- blk-mq freeze helpers and queue flags.

Filesystem/block relevance:
- Provides throttling and latency feedback hooks that can shape filesystem writeback and application I/O behavior.
