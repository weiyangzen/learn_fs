# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_events.h

Purpose: Declares the driver event types, event descriptors, and queue/list structures used for DFC/HBA/SAN diagnostic event delivery.

Key definitions:
- `emlxs_event_t`: event descriptor containing mask bit, label, timeout, and destroy callback.
- `DEFINE_EVT(...)`: dual-use macro that either defines or declares event globals depending on `DEF_EVENT_STRUCT`.
- Event masks include link, RSCN, CT, multipulse, dump, temperature, virtual-port RSCN, async, FCoE, and optional SAN diagnostic classes.
- Predefined event descriptors include `emlxs_link_event`, `emlxs_rscn_event`, `emlxs_ct_event`, `emlxs_dump_event`, `emlxs_temp_event`, `emlxs_fcoe_event`, and `emlxs_async_event`.
- `emlxs_event_entry_t`: doubly linked event queue element with ID, timestamp, timer, event type, port pointer, context buffer, size, and completion flags.
- `emlxs_event_queue_t`: protected queue with mutex, condition variable, per-event `last_id`, global `next_id`, count, and first/last pointers.

Dependencies and interactions:
- Requires `kmutex_t`, `kcondvar_t`, and the driver event implementation.
- `emlxs_extern.h` declares event queue creation/destruction, event logging, DFC event retrieval, and SAN diagnostic event routines.
- `emlxs_hba_t` owns `event_queue`, event masks, timers, and DFC/HBA event state.

Implementation notes:
- `EVT_TIMEOUT_DEFAULT` is 60, `EVT_TIMEOUT_NEVER` is 0, and the default destroy callback is `emlxs_null_func`.
- CT events have a custom destroy hook, `emlxs_ct_event_destroy`, reflecting payload ownership needs.
