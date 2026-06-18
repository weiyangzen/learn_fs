# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fm.c

## Purpose

`fm.c` provides kernel Fault Management Architecture support for ereport posting, FMA nvlist allocation, FMRI construction, ENA manipulation, panic banners, and crash-dump persistence of pending ereports.

Read completely: 1,384 lines.

## Main Responsibilities

- Initializes the kernel ereport sysevent channel and error queue in `fm_init()`.
- Drains queued ereports to sysevents or console output during panic.
- Prints compact nvlist telemetry through `fm_nvprint()` and `fm_nvprintr()`.
- Implements `fm_panic()`, `is_fm_panic()`, and `fm_banner()` for FMA-driven fatal errors.
- Writes pending ereports to the dump device through `fm_ereport_dump()`.
- Posts ereports to `FM_ERROR_CHAN` through `fm_ereport_post()`.
- Provides FMA-specific nvlist allocator wrappers.
- Builds standard ereport payloads and FMRIs for hc, dev, cpu, mem, and ZFS schemes.
- Generates and decodes ENA values.
- Converts stack program counters into symbolic payload strings.

## Event And Dump Flow

`fm_init()` binds `FM_ERROR_CHAN`, sizes the error queue, allocates a dump buffer, and installs kstats for dropped or malformed telemetry.

`fm_drain()` is the error queue drain callback. During normal operation it posts the nvlist to the sysevent channel. During panic it prints the nvlist to the console.

`fm_ereport_dump()` drains the error queue outside panic, then walks the sysevent channel and writes `erpt_dump_t` headers plus encoded event buffers to the dump device. It records checksums, event sizes, high-resolution timestamps, and wall-clock bases.

## Panic Behavior

`fm_panic()` records a panic format string atomically, disables fast reboot on x86, and calls `vpanic()`.

`fm_banner()` emits the special FMA panic message with `SUNOS-8000-0G`, platform, host, source version, event time, and recommended action. It intentionally uses console output for most text and `cmn_err()` only for the log summary.

## Nvlist And Payload Construction

`fm_nvlist_create()` creates nvlists using either the default kernel allocator or a caller-supplied fixed-buffer allocator. `fm_nvlist_destroy()` optionally frees or retains the allocator.

`i_fm_payload_set()` is the varargs payload encoder. It supports scalar values, arrays, strings, nested nvlists, and nvlist arrays for the nvpair types used by FMA.

`fm_ereport_set()` builds a category-1 ereport with class, ENA, detector, and extra payload members.

## FMRI Builders

The file provides scheme-specific helpers:

- `fm_fmri_hc_set()` and `fm_fmri_hc_create()` for hierarchical-component FMRIs.
- `fm_fmri_dev_set()` for device-path FMRIs.
- `fm_fmri_cpu_set()` for CPU FMRIs.
- `fm_fmri_mem_set()` for memory FMRIs.
- `fm_fmri_zfs_set()` for ZFS pool/vdev FMRIs.

Failures increment `erpt_kstat_data.fmri_set_failed` or related counters rather than panicking.

## ENA Helpers

`fm_ena_generate_cpu()`, `fm_ena_generate()`, `fm_ena_increment()`, `fm_ena_generation_get()`, `fm_ena_format_get()`, `fm_ena_id_get()`, and `fm_ena_time_get()` implement formats 1 and 2 of the Event Numeric Association field.

## Important Invariants

- Ereports larger than `ERPT_DATA_SZ` or with zero encoded size are dropped.
- FMA nvlist creation with default allocation may sleep and is only valid in passive kernel contexts.
- Fixed-buffer allocators exist for constrained contexts.
- Some FMRIs require exact protocol versions; version mismatch increments failure kstats.

## Research Relevance

For filesystem/storage work, the ZFS FMRI helper and ereport posting path are the key pieces. This file defines how kernel storage faults can be encoded, queued, persisted to crash dumps, and later consumed by FMA tooling.
