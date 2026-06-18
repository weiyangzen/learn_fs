# File Research: sources/virtualization/libblockdev/src/plugins/nvme/nvme-info.c

## Purpose

Implements NVMe information retrieval and GLib object lifecycle helpers for controller, namespace, SMART, error log, self-test log, and sanitize log data.

## Main Responsibilities

- Provide free/copy helpers for all public NVMe data structs.
- Open NVMe devices and allocate page-aligned ioctl buffers.
- Translate libnvme Identify Controller data to `BDNVMEControllerInfo`.
- Translate Identify Namespace and namespace descriptor data to `BDNVMENamespaceInfo`.
- Translate SMART / Health, Error Information, Device Self-test, and Sanitize log pages.
- Convert NVMe status fields into embedded `GError` values where public structs expose command-specific errors.

## Important Functions

- `bd_nvme_controller_info_free()` / `bd_nvme_controller_info_copy()` manage strings in controller info.
- `bd_nvme_namespace_info_free()` / `bd_nvme_namespace_info_copy()` deep-copy namespace IDs and LBA format arrays.
- `bd_nvme_error_log_entry_copy()` and `bd_nvme_self_test_log_entry_copy()` deep-copy embedded `GError`.
- `bd_nvme_self_test_result_to_string()` maps self-test result enum values to stable identifier strings.
- `_open_dev()` opens a device read-only and maps open failures through `_nvme_status_to_error()`.
- `_nvme_alloc()` allocates zeroed, page-aligned memory rounded to 4 KiB.
- `bd_nvme_get_controller_info()` issues Identify Controller and translates features, capacities, names, firmware, NVMe revision, self-test and sanitize capabilities.
- `bd_nvme_get_namespace_info()` issues Identify Namespace, optional descriptor list for NVMe 1.3+, optional independent namespace info for NVMe 2.0+, and builds LBA format metadata.
- `bd_nvme_get_smart_log()` reads SMART data and controller temperature thresholds.
- `bd_nvme_get_error_log_entries()` sizes the error log from `elpe`, reads all entries, and returns only entries with nonzero `error_count`.
- `bd_nvme_get_self_test_log()` reads current self-test progress and recent self-test results.
- `bd_nvme_get_sanitize_log()` reads sanitize state, progress, pass count, and time estimates.

## Dependencies and Interactions

- Uses libnvme ioctl helpers such as `nvme_identify_ctrl()`, `nvme_get_nsid()`, `nvme_identify_ns()`, `nvme_identify_ns_descs()`, `nvme_get_log_smart()`, `nvme_get_log_error()`, `nvme_get_log_device_self_test()`, and `nvme_get_log_sanitize()`.
- Uses shared `_nvme_status_to_error()` from `nvme-error.c`.
- Public struct definitions and enum mappings come from `nvme.h`.

## Notable Details

- 128-bit NVMe counters are reduced to `guint64`; the helper explicitly notes possible overflow.
- Controller model, serial, firmware, and subsystem NQN fields are stripped of trailing padding.
- Namespace descriptor parsing prefers descriptor-list EUI64/NGUID/UUID values and falls back to legacy Identify Namespace fields.
- SMART data units are converted to bytes using NVMe’s `1000 * 512` unit definition.
- Sanitize time estimate fields use `-1` when the device reports `0xffffffff`.
- LBA format relative performance is stored as `rp + 1` to match the public enum’s nonzero values.
