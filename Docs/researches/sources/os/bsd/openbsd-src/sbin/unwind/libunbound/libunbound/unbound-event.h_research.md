# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/unbound-event.h

Public libunbound header for integrating resolution with caller-provided event systems.

Defines:
- Event bit constants: timeout, read, write, signal, persist.
- `UB_EVENT_MAGIC` version guard for pluggable event objects.
- `struct ub_event_base_vmt`: virtual methods for event-base free, dispatch, loopexit, event creation, signal creation, and Windows WSA event registration.
- `struct ub_event_base`: magic plus base vtable.
- `struct ub_event_vmt`: methods to add/delete bits, set fd, free, activate/deactivate, manage timers/signals, handle Windows WSA events, and signal TCP would-block state.
- `struct ub_event`: magic plus event vtable.
- `ub_event_callback_type`: callback receiving user data, rcode, packet pointer/length, DNSSEC status, bogus reason, and rate-limit status.

Public API:
- `ub_ctx_create_ub_event()` creates a libunbound context on a generic pluggable event base.
- `ub_ctx_create_event()` creates a context on libevent’s `event_base`.
- `ub_ctx_set_event()` swaps the libevent base and cancels outbound queries.
- `ub_resolve_event()` submits an asynchronous resolution using the configured event base.

Role:
- Lets applications run libunbound state machines inside their own event loop without a worker thread or forked process.
- Documents that event callbacks receive internal buffers that must not be freed or modified.
