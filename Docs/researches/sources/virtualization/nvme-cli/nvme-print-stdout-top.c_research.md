# File Research: sources/virtualization/nvme-cli/nvme-print-stdout-top.c

## Purpose

`nvme-print-stdout-top.c` implements the interactive stdout `nvme top` dashboard. It scans libnvme topology, gathers per-namespace and per-path I/O statistics, formats metrics into tables, and drives an interactive terminal dashboard with refresh, scrolling, subsystem selection, subsystem detail screens, uevent rescans, and resize handling.

## Main Entry Point

- `stdout_top(int refresh_interval)` initializes topology and dashboard state, builds the subsystem selection array, resets counters, runs the main event loop, and exits the dashboard on quit or error.

## Metric Calculation

The top of the file provides small helpers for deriving dashboard metrics from libnvme counters:

- Utilization: `nvme_calc_util_percent()`, `nvme_path_calc_util_percent()`, `nvme_ns_calc_util_percent()`.
- IOPS: `nvme_calc_iops()`, path and namespace read/write wrappers.
- Latency: `nvme_calc_latency()`, path and namespace read/write wrappers.
- Bandwidth: `nvme_calc_bandwidth()`, path and namespace read/write wrappers.
- Formatting: `nvme_format_iops()`, `nvme_format_bw()`, `nvme_format_lat()`.

The calculation code uses libnvme stat intervals in milliseconds, suppresses IOPS/bandwidth if the interval is under one second, assumes 512-byte sectors for bandwidth, and computes latency as ticks divided by I/O count.

## Aggregation Paths

Two aggregation styles are used:

- `nvme_ns_calc_aggr_stat()` and `nvme_path_calc_aggr_stat()` add read/write IOPS and bandwidth while tracking maximum read latency, write latency, and utilization.
- `nvme_ns_calc_stat()` and `nvme_path_calc_stat()` compute a single namespace/path row, including inflight I/O.

These helpers are used by subsystem summary tables, namespace tables, path performance tables, and controller summaries.

## Table Rendering

The file uses `util/table.h` to build stdout tables:

- `stdout_top_print_path_health()` prints per-path ANA state, retry count, failover count, and command error count.
- `stdout_top_print_ctrl_summary()` prints per-controller transport, address, state, resets, optional reconnects, errors, IOPS, latency, bandwidth, and utilization.
- `stdout_top_print_ns_stat()` prints namespace stats for non-multipath subsystems.
- `stdout_top_print_nshead_stat()` prints namespace-head stats for multipath subsystems.
- `stdout_top_print_path_perf()` prints per-path performance and includes I/O-policy-specific `Nodes` or `Qdepth` columns.
- `stdout_top_draw_subsys_screen()` prints the top-level subsystem summary table and footer.

Column filtering is used in two places:

- `stdout_top_print_ctrl_summary_tbl_filter()` hides `Paths` when not multipath and hides `Reconnects` for non-fabrics controllers.
- `subsystem_iopolicy_filter()` is referenced from elsewhere to hide/show path performance columns based on subsystem I/O policy.

## Topology And Stat Refresh

The topology is libnvme-backed:

- `stdout_top_rescan_topology()` creates a global libnvme context and scans current topology.
- `stdout_top_search_subsystem()` finds a subsystem by name after rescan.
- `stdout_top_build_subsys_arr()` builds an array of subsystem handles for selection.
- `stdout_top_find_subsys_by_name()` restores selection after topology changes.
- `stdout_top_update_stat()` updates namespace/path stats, using path stats only for multipath subsystems.
- `stdout_top_reset_stat()` resets namespace/path stat baselines before the dashboard loop starts.

This design lets the dashboard recompute deltas between refresh frames and recover from NVMe topology uevents.

## Interactive Dashboard Flow

`stdout_top()` runs a two-level UI:

1. Top-level subsystem summary screen:
   - Shows all subsystems.
   - Up/down changes selected row.
   - Enter opens the selected subsystem.
   - Timeout refreshes.
   - NVMe uevent rescans topology and attempts to keep selection by subsystem name.
   - SIGWINCH redraws.
   - `q` exits.

2. Subsystem topology/detail screen:
   - Implemented by `stdout_top_draw_subsys_topology_screen()`.
   - Rescans topology and finds the chosen subsystem by name.
   - Prints header, subsystem topology/config, stat tables, and footer.
   - ESC returns to subsystem selection.
   - Up/down scrolls the frame buffer.
   - Timeout refreshes.
   - NVMe uevent rescans and returns to selection if the subsystem disappeared.
   - `q` or dashboard error exits.

`stdout_top_print_subsys_topology()` decides whether to render multipath-specific namespace-head/path tables or non-multipath namespace stats, then always prints controller summary.

## Output Layout

The dashboard writes to a `FILE *stream` returned by `dashboard_init()`. It manually informs the dashboard about header/footer row counts so scrolling and reverse-video highlighting work correctly. The top-level screen highlights the selected subsystem row. Detail screens use a fixed header showing refresh interval and a footer showing ESC/quit instructions.

## Dependencies

This file depends on:

- `libnvme.h` for topology handles, stat counters, update/reset APIs, and subsystem/controller/path/namespace attributes.
- `nvme.h`, `nvme-print.h`, `common.h`, and `logging.h` for shared nvme-cli helpers, error output, cleanup attributes, and topology helpers such as `nvme_is_multipath()`.
- `util/dashboard.h` for terminal frame rendering, events, scrolling, resize handling, and uevent delivery.
- `util/table.h` for table construction, filtered columns, row formatting, and stream printing.

## Notable Implementation Details

- PCIe/fabrics detection is string-based: controllers whose transport is not `"pcie"` are treated as fabrics.
- The controller summary uses the first controller in a subsystem to decide whether the `Reconnects` column is shown.
- NUMA node `"-1"` is displayed as `NUMA_NO_NODE`.
- The subsystem detail screen rescans topology before display and on uevents, avoiding stale libnvme handles.
- The top-level loop stores the selected subsystem name before rescan so it can restore focus after topology changes.
- Most table allocation failures produce `nvme_show_error()` and unwind through `table_free()`.

## Risks And Maintenance Notes

- Metric units depend on kernel/libnvme counter semantics. Bandwidth assumes 512-byte sectors.
- IOPS and bandwidth intentionally report zero for intervals below one second; short refresh intervals may look inactive.
- Several event-loop branches use `goto draw` / `goto wait_for_event` to preserve scroll behavior. Changes should be tested interactively.
- The first-controller heuristic for fabrics/reconnect column visibility may be inaccurate for mixed-transport subsystems.
- Topology handles are invalidated on rescan; the code generally handles this by searching by subsystem name, and future changes should preserve that pattern.
