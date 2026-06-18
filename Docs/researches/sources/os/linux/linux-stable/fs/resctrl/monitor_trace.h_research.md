# File Research: sources/os/linux/linux-stable/fs/resctrl/monitor_trace.h

Defines the resctrl tracepoint header for monitor limbo accounting.

Key element:
- `TRACE_EVENT(mon_llc_occupancy_limbo)` records `ctrl_hw_id`, `mon_hw_id`, domain id, and LLC occupancy bytes while limbo RMIDs are checked.

Usage:
- Included by `monitor.c` with `CREATE_TRACE_POINTS`.
- Emitted from `__check_limbo()` after LLC occupancy reads.

Purpose:
- Provides observability into why RMIDs remain dirty or become reusable.
