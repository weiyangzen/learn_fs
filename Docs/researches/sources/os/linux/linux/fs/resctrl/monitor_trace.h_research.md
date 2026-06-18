# File Research: sources/os/linux/linux/fs/resctrl/monitor_trace.h

## Purpose
Defines the resctrl tracepoint used when checking dirty RMIDs in LLC occupancy limbo.

## Main Trace Event
- `mon_llc_occupancy_limbo`
  - Arguments: `ctrl_hw_id`, `mon_hw_id`, `domain_id`, `llc_occupancy_bytes`.
  - Emitted from `monitor.c::__check_limbo()` after a successful LLC occupancy read.
  - Helps diagnose why RMIDs remain dirty or become reusable.

## Integration
- `TRACE_SYSTEM` is `resctrl`.
- `TRACE_INCLUDE_PATH` is local directory and `TRACE_INCLUDE_FILE` is `monitor_trace`.
- Included by `monitor.c` after `#define CREATE_TRACE_POINTS`.

## Research Notes
This file is small but important for observability of RMID recycling. It does not alter behavior; it provides a stable trace schema for monitoring limbo occupancy decisions.
