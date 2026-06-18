# File Research: sources/virtualization/spdk/lib/trace/trace_internal.h

This private trace header declares the internal functions shared between the trace core, trace flags, and trace RPC layer.

It exposes `trace_get_shm_name()` for reporting the active shared-memory object name, plus `trace_flags_init()` and `trace_flags_fini()` for trace definition registration and owner-id allocator lifecycle.

The header intentionally keeps the internal surface small; public trace data structures and APIs come from `spdk/trace.h`.
