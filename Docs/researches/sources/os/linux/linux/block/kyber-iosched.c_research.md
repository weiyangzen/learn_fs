# File Research: sources/os/linux/linux/block/kyber-iosched.c

Implements the Kyber blk-mq I/O scheduler, a latency-control scheduler that throttles per-domain queue depth using scalable bitmaps and latency feedback.

Key responsibilities:
- Classifies requests into read, write, discard, and other scheduling domains.
- Limits each domain with `sbitmap_queue` tokens.
- Maintains per-CPU latency histograms for total and device I/O latency.
- Periodically calculates p90/p99 latency buckets and resizes domain token depths.
- Uses per-hctx/per-context queues to preserve merge opportunities and scalable insertion.
- Dispatches requests in domain batches while respecting token availability.

Important structures:
- `struct kyber_queue_data` stores queue-wide tokens, latency targets, per-CPU latency, and timer state.
- `struct kyber_hctx_data` stores per-hctx request queues, current domain, batching, context maps, and wait entries.
- `struct kyber_ctx_queue` stores per-context domain request lists under a spinlock.

Important functions:
- `kyber_timer_fn()` aggregates latency samples and adjusts depths.
- `kyber_init_sched()` / `kyber_exit_sched()` enable/disable accounting and scheduler state.
- `kyber_init_hctx()` / `kyber_exit_hctx()` manage per-hctx scheduler data.
- `kyber_insert_requests()` queues requests by domain/context.
- `kyber_dispatch_request()` rotates through domains and batches dispatch.
- `kyber_completed_request()` records latency samples and schedules adjustment.
- `kyber_get_domain_token()` integrates token acquisition with sbitmap wait queues.

Interfaces:
- Sysfs exposes read/write latency targets.
- Debugfs exposes token state, per-domain request lists, wait state, current domain, and batching.
- Registers as elevator `"kyber"`.

Research relevance:
- Kyber is a concrete example of blk-mq scheduling focused on latency feedback rather than purely positional ordering.
