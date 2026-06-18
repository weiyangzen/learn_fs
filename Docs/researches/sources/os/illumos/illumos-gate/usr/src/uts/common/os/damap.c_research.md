# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/damap.c

## Purpose

`damap.c` implements device address maps. A DAM tracks provider-reported string addresses, waits for reports to stabilize, activates newly stable addresses, deactivates addresses that disappear, and lets class drivers look up active address IDs.

It supports two reporting modes:

- `DAMAP_REPORT_PERADDR`: providers report individual address additions and deletions.
- `DAMAP_REPORT_FULLSET`: providers report a complete address set between begin/end calls.

## Map Creation And Allocation

`damap_create()` allocates a lightly backed map, records callbacks, initializes locks, condition variables, bitsets, options, stabilization timing, and returns a `damap_t`.

Major backing resources are allocated lazily by `dam_map_alloc()` on first report. It creates:

- Soft-state storage for `dam_da_t` address records.
- A string-to-ID table through `ddi_strid`.
- Per-map kstats.
- Bitsets for active, stable, and report sets.

The map grows in `DAM_SIZE_BUMP` chunks when IDs exceed the current bitset capacity.

`damap_destroy()` marks the map destroy-pending, synchronizes pending activity, cancels timers, deactivates stable addresses, releases unstable entries directly, destroys string IDs/soft state/kstats/bitsets, and frees the map.

## Stabilization And Synchronization

`damap_sync()` waits until no full-set update, stabilization pass, report-set entries, or scheduled timeout remains. With a nonzero timeout it can return 0 on timeout. After apparent quiescence, it waits one stabilization interval and checks again to avoid racing with late report activity.

Stabilization is timer-driven. Per-address reports use `dam_addr_stable_cb()`. Full-set reports use `dam_addrset_stable_cb()`. Both eventually dispatch `dam_stabilize_map()` on `system_taskq`.

`dam_stabilize_map()` compares the current active set and computed stable set, derives activation and deactivation bitsets, drops the map lock while invoking callbacks, then updates stable-cycle counters and active kstats.

## Per-Address Reporting

`damap_addr_add()` reports an address addition. It validates mode, allocates backing resources, gets or creates an address ID, clears any existing pending report as jitter, stores provider-private data and optional nvlist, then calls `dam_addr_report(..., RPT_ADDR_ADD)`.

`damap_addr_del()` reports removal. Missing addresses are treated as success. Existing pending reports are released as jitter, then a delete report is queued through `dam_addr_report(..., RPT_ADDR_DEL)`.

`dam_addr_report()` timestamps the report, sets a deadline based on `ddi_get_lbolt64() + dam_stable_ticks`, records add/delete intent with `DA_RELE`, adds the ID to the report set, and schedules the stabilization timeout.

`dam_addr_report_release()` cancels a pending report, optionally calls the provider deactivation callback for unstable private data, clears provider-private data, and frees the report nvlist.

## Full-Set Reporting

`damap_addrset_begin()` starts a full-set report and sets `DAM_SETADD`. It flushes any already pending full-set activity first.

`damap_addrset_add()` adds addresses to the pending report set while `DAM_SETADD` is active. It creates IDs as needed, handles jitter by releasing previous pending report data, stores provider-private data and optional nvlist, and returns the address ID.

`damap_addrset_end()` either resets pending report state when `DAMAP_END_RESET` is requested or schedules full-set stabilization using `dam_addrset_stable_cb()`.

`damap_addrset_flush()` cancels a pending full-set report and releases pending address report data.

In full-set stabilization, the report set becomes the new stable set, then active/stable deltas drive activation and deactivation.

## Lookup And Reference Management

Active addresses can be queried through:

- `damap_lookup()`: returns and references a stable active ID by address string.
- `damap_lookup_all()`: returns a bitset list of all active IDs and references each.
- `damap_id_next()`: iterates an ID list.
- `damap_id_list_rele()`: releases all IDs in a list.
- `damap_id_rele()`: releases one referenced ID.
- `damap_id_ref()`: returns the current reference count.
- `damap_id2addr()` and `damap_id2nvlist()`: map IDs to address strings and active nvlists.
- `damap_id_priv_set()` and `damap_id_priv_get()`: manage class-driver private data per address.

`dam_addr_release()` frees an address ID only when no outstanding references remain and no report is pending.

## Activation And Deactivation

`dam_addr_activate()` marks an address active, moves the reported nvlist into the stable nvlist slot, calls the provider activation callback if present, then invokes the class configuration callback. If configuration fails, it marks `DA_FAILED_CONFIG` and immediately deactivates with reason `DAMAP_DEACT_RSN_CFG_FAIL`.

`dam_addr_deactivate()` invokes the class unconfiguration callback and then calls `dam_deact_cleanup()`.

`dam_deact_cleanup()` invokes the provider deactivation callback if present, clears active state and stored nvlists/private data, then releases the address.

`dam_addrset_activate()` and `dam_addrset_deactivate()` can run serially or create temporary taskqs for multithreaded configuration when `DAMAP_MTCONFIG` is set.

## Timers And Taskq Behavior

`dam_sched_timeout()` manages a single map timeout. It cancels with `untimeout()` when requested and schedules a timeout only if none is active.

`dam_addr_stable_cb()` scans pending per-address reports, computes which deadlines have passed, dispatches `dam_stabilize_map()` only when handoff succeeds, and reschedules for the next nearest deadline or short retry delay after taskq dispatch failure.

`dam_addrset_stable_cb()` handles full-set stabilization. If a stabilization pass is already active or taskq dispatch fails, it counts overrun and retries after `damap_taskq_dispatch_retry_usec`.

## Kstats

`dam_kstat_create()` creates per-map kstats under module `dam`, class `damap`, with counters:

- `cycles`
- `overrun`
- `jitter`
- `active`

Macros update these counters when the kstat exists.

## Dependencies

The file depends on:

- `ddi_strid` for string-to-ID mapping.
- DDI soft state for per-address records.
- `bitset_t` for active/stable/report sets.
- `timeout`, `untimeout`, `system_taskq`, and optional temporary taskqs.
- DTrace probes, kstats, nvlists, and DDI timing helpers.

## Research Notes

The core invariant is that provider report churn is not immediately exposed. Reports first enter `dam_report_set`, then stabilize into a computed stable set, then activate/deactivate callbacks are invoked outside `dam_lock`. Audit hotspots include report jitter handling, reference counts during deactivation, full-set flush/reset semantics, timeout cancellation while callbacks race, and taskq dispatch failure recovery.
