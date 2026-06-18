# File Research: sources/virtualization/spdk/lib/trace/trace_rpc.c

This file exposes JSON-RPC controls for SPDK tracing.

`trace_set_tpoint_mask` and `trace_clear_tpoint_mask` decode a trace group name and 64-bit tracepoint mask, map the group name to a single group bit, convert that bit to a group ID with `spdk_u64log2()`, and update that group’s mask. `trace_enable_tpoint_group` and `trace_disable_tpoint_group` decode a group name and enable or disable all tracepoints for that group, including the special `"all"` group handled by trace flags.

`trace_get_tpoint_group_mask` returns the aggregate enabled group mask plus a per-group object containing whether the group is enabled, the group mask bit, the current tracepoint mask, and all named tracepoints with local IDs and enabled state. It walks registered trace groups and the tracepoint section.

`trace_clear` requires no parameters and records the current clear timestamp through `spdk_trace_clear()`. `trace_get_info` reports the `/dev/shm...` tracepoint shared-memory path, aggregate group mask, and per-group mask data.

All RPCs are registered for runtime use; most are also valid at startup. Parameter validation is strict for missing names and unexpected parameters. The file assumes `g_trace_file` is valid for introspective RPCs; `trace_get_tpoint_group_mask` directly reads the tracepoint section while iterating groups.
