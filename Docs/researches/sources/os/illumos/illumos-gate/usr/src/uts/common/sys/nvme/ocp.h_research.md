# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/ocp.h

## Purpose

`nvme/ocp.h` defines uncommitted vendor-specific NVMe interfaces for the OCP Datacenter NVMe SSD specifications, covering versions 2.0 and 2.5 and the earlier Cloud SSD lineage.

## Main Interfaces

`ocp_vul_t` defines OCP log IDs for SMART, error recovery, firmware activation, latency monitor, device capabilities, unsupported requirements, TCG configuration, and telemetry strings. `ocp_vuf_t` defines OCP feature IDs for error injection, clearing firmware activation history, EOL/PLP behavior, PCIe correctable error clear, IEEE1667, latency monitor, PLP health, power state, telemetry profile, and async events.

All payload structures are packed and little-endian. Major log structures include:

- `ocp_vul_smart_t`: 512-byte SMART/health log with physical media reads/writes, NAND block health, recovery/error counters, erase counts, thermal throttling, DSSD version, PCIe errors, incomplete shutdowns, free percentage, capacitor health, unaligned I/O, security version, namespace utilization, PLP events, endurance estimate, retrains, power-state changes, min firmware rollback, version, and GUID.
- `ocp_vul_errrec_t`: 512-byte error recovery log with reset timing, panic reset actions, device recovery actions, panic IDs, vendor recovery command fields, secondary recovery, old panic IDs, version, and GUID.
- `ocp_vul_fwact_t`: 4096-byte firmware activation history log with 20 fixed 64-byte entries.
- `ocp_vul_lat_t`: 512-byte latency monitor log with active/static bucket counters, latency timestamps, measured latency, debug trigger metadata, version, and GUID.
- `ocp_vul_devcap_t`: 4096-byte capability log including power-state descriptors and capability bitfields.
- `ocp_vul_unsup_req_t`: 4096-byte unsupported requirements log with 253 fixed 16-byte requirement strings.
- `ocp_vul_telstr_t` and table-entry structures for OCP 2.5 telemetry string logs.

Associated enums define reset-action bits, recovery-action bits, device capability bits, latency monitor feature/configuration bits, and capability flags for out-of-band, write-zeroes, dataset management, write-uncorrectable, and fused operations.

## Runtime Use

Vendor-specific headers alias device-family log IDs to these OCP constants. Consumers request the log page, verify version/GUID where appropriate, and parse the packed payload. Several logs carry variable-length trailing data or string tables, so consumers must use header offsets and lengths rather than assuming null-terminated strings.

## Dependencies

Includes `sys/isa_defs.h`, `sys/debug.h`, `sys/stdint.h`, and `sys/stddef.h`. Uses endian bitfield guards and extensive `CTASSERT()` checks.

## Risks and Invariants

All structures are hardware/spec ABI mirrors. Packing, little-endian interpretation, structure sizes, offsets, version values, and GUIDs are critical.

String-like fields are often byte arrays, fixed-width, padded, or counted; they must not be treated as trusted C strings.

The unsupported-requirements strings are explicitly untrusted byte arrays and may not be null-terminated.

A duplicate `CTASSERT(offsetof(ocp_vul_errrec_t, oer_npanic) == 31)` appears twice; it is harmless but redundant.
