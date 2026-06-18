# File Research: sources/virtualization/spdk/lib/trace/trace_flags.c

This file manages tracepoint group registration, trace masks, tracepoint metadata, owner/object metadata, and owner-id allocation.

Trace masks live in the trace shared-memory tpoint-mask section. `spdk_trace_get_tpoint_mask()`, `spdk_trace_set_tpoints()`, and `spdk_trace_clear_tpoints()` operate on one group; group-mask helpers enable or disable all tracepoints in selected groups. `spdk_trace_create_tpoint_mask()` maps a tracepoint name to its bit inside a group, while `spdk_trace_create_tpoint_group_mask()` maps a group name, or `"all"`, to a group bitmask.

Registration functions are accumulated in `g_reg_fn_head` by `spdk_trace_add_register_fn()`, which rejects missing names, the reserved name `"all"`, duplicate group IDs, and duplicate names, then keeps the list sorted by group ID. `trace_flags_init()` invokes each registered function so modules can populate tracepoint definitions after the trace file exists.

Trace metadata registration writes into shared sections. `spdk_trace_register_owner_type()` and `spdk_trace_register_object()` register display prefixes. `spdk_trace_register_description_ext()` copies tracepoint names, object/owner types, new-object markers, and argument descriptors with type/size validation. The older `spdk_trace_register_description()` wrapper registers a single 64-bit argument. `spdk_trace_tpoint_register_relation()` records relationships between tracepoint arguments and object types for parser correlation.

Owner IDs are allocated from a spinlock-protected ring. IDs start at 256, reserving 0 for no-owner and avoiding collisions with legacy poller IDs. `spdk_trace_register_owner()` stamps type, timestamp, and description; unregister returns the ID to the ring; description setters can replace or append text. These APIs are no-ops in unit-test contexts where the ring is not initialized.

`spdk_trace_mask_usage()` prints CLI usage text listing registered trace groups and mask syntax. `spdk_trace_clear()` records `clear_tsc`, which parsers use to suppress older events.

Key invariants are unique sorted trace groups, valid tracepoint IDs and argument shapes, owner ring balance, and shared-memory initialization before metadata writes. The owner description helper assumes `description` is non-null and formats into a fixed per-owner description region.
