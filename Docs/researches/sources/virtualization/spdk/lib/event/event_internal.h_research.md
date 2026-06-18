# File Research: sources/virtualization/spdk/lib/event/event_internal.h

Internal header shared by event framework sources.

Important contents:
- Defines `struct spdk_lw_thread`, the reactor-side context attached to each SPDK thread.
- Tracks current and initial lcore, reschedule flag, scheduling timestamp, lifetime stats, and current scheduling-period stats.
- Declares `app_get_proc_stat()` for OS CPU usage deltas.
- Declares scheduler isolated-core-mask getters/setters.

Role: connects `reactor.c`, `app.c`, scheduler code, and framework RPC reporting without exposing these details as public API.
