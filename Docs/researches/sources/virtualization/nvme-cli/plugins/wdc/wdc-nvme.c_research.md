# File Research: sources/virtualization/nvme-cli/plugins/wdc/wdc-nvme.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-7532, source bytes 262124, report `Docs/researches/chunks/chunk_sources_virtualization_nvme_cli_plugins_wdc_wdc_nvme_c_1_1_7532_6435643d1400_research.md`
- chunk 2: lines 7533-12905, source bytes 171193, report `Docs/researches/chunks/chunk_sources_virtualization_nvme_cli_plugins_wdc_wdc_nvme_c_2_7533_12905_f4fab7f21789_research.md`

## Chunk Research

### Chunk 1: lines 1-7532

# Chunk Research: sources/virtualization/nvme-cli/plugins/wdc/wdc-nvme.c lines 1-7532

## Scope

This chunk covers the first half of the Western Digital/SanDisk `nvme-cli` vendor plugin implementation. It defines the device ID matrix, capability bitmask model, WDC/OCP/vendor log page wire formats, UUID constants, helper probes, diagnostic/internal-log dump flows, crash/drive/pfail dump commands, purge commands, C0/C1/C3/C4/C5/CA/D0/firmware-history printers, and the beginning of CA log retrieval. The source tree `sources/virtualization/nvme-cli` is included by `Docs/research_subset_a.md`.

## APIs and Entry Points

- User-visible command handlers in this range include `wdc_cap_diag()`, `wdc_vs_internal_fw_log()`, `wdc_drive_log()`, `wdc_get_crash_dump()`, `wdc_get_pfail_dump()`, `wdc_id_ctrl()`, `wdc_purge()`, and `wdc_purge_monitor()`.
- Device identification and gating helpers are `wdc_get_pci_ids()`, `wdc_get_vendor_id()`, `wdc_check_device()`, `wdc_get_drive_capabilities()`, and `wdc_get_enc_drive_capabilities()`.
- Log support discovery uses NVMe Supported Log Pages first, then WDC C2 device-management entries.
- Dump retrieval primitives use libnvme admin passthrough and standard get-log/telemetry helpers, then write binary output files.

## Core Control Flow

Most command handlers parse CLI options, open an NVMe transport, scan topology, validate WDC/SanDisk vendor support, compute a capability bitmask, and dispatch only if the required capability is present.

Capability detection is a large vendor/device switch. Some devices receive fixed capability masks; others probe log-page support dynamically and use customer firmware ID or C2 marketing-name strings to choose OCP-style features.

Diagnostics can use vendor opcode `0xE6`, DUI opcode `0xFA`, standard NVMe telemetry, or SN730-specific VUC log chunking. Crash and pfail commands fetch a dump length, read the dump, write it, then clear the dump. Purge sends opcode `0xDD`; purge monitor sends opcode `0xDE` and decodes state/progress.

## State and Dependencies

The central state model is the 64-bit `WDC_DRIVE_CAP_*` bitmask. Wire-format structs mirror NVMe/vendor/OCP payloads for C2, E6, DUI variants, SMART/performance logs, OCP C1/C4/C5, firmware activation history, hardware revision, NAND, and PCIe stats.

Dependencies include libnvme transport/identify/get-log/telemetry/admin-passthru APIs, nvme-cli parsing/printing/JSON helpers, WDC utility headers, sysfs PCI ID files, POSIX file APIs, endian conversion helpers, and shell `tar` for archived outputs.

## Risks and Edge Cases

- C2 string parsing copies device-reported lengths into caller buffers without explicit destination-size checks.
- Archive commands pass user-influenced paths to `system()`, making shell quoting/security sensitive.
- Several printers cast byte arrays to integer pointers, which can be alignment-sensitive.
- Capability detection is a hard-coded matrix and can silently miss newer devices/firmware.
- Some JSON printers appear to emit mismatched fields.
- Dump paths allocate based on device-reported sizes.
- V1 DUI section parsing trusts `section_count` without clamping to the fixed array size.

## Cross-Chunk References

- `wdc_get_ca_log_page()` starts here and continues after line 7532.
- Later chunks consume helpers defined here for C1/C3/C4/C5, CA/D0, firmware history, cloud SMART, hardware revision, NAND/PCIe stats, drive status, clear commands, reason ID, drive essentials, resize, enclosure logs, and latency-monitor feature setting.
- Helpers referenced but implemented later include `wdc_get_fw_cust_id()`, drive essentials, resize, drive info, reason ID, enclosure log helpers, and public `run_wdc_*` wrappers.

### Chunk 2: lines 7533-12905

# Chunk Research: sources/virtualization/nvme-cli/plugins/wdc/wdc-nvme.c lines 7533-12905

Scope: `Docs/research_subset_a.md` includes `sources/virtualization/nvme-cli`. This report covers only the requested chunk of `plugins/wdc/wdc-nvme.c`; the chunk starts mid-function in `wdc_get_ca_log_page()` and ends with external `run_wdc_*` wrappers.

## API Surface Covered

- Vendor/OCP log retrieval helpers: C1 performance, C3 latency monitor, OCP C1/C4/C5, and D0 SMART log readers.
- Cloud SMART formatting: `le_to_float()`, GUID/status stringifiers, and normal/JSON printers for `struct ocp_cloud_smart_log`.
- User-facing plugin commands: SMART/log retrieval, OCP logs, clear/status commands, FW activation history, telemetry options, Drive Essentials export, resize, reason identifier, log-page directory, drive info, temperature stats, capabilities/version, enclosure logs, and latency monitor feature setting.
- External wrappers: `run_wdc_*()` functions expose static command implementations, plus helpers for customer id, supported log-page checks, and drive capabilities.

## Control Flow and Behavior

- Most commands follow: `parse_and_open()` -> `libnvme_scan_topology()` -> `wdc_check_device()`/`wdc_get_drive_capabilities()` -> NVMe get-log/set-feature/admin passthrough -> normal/JSON/binary output.
- `wdc_vs_smart_add_log()` multiplexes C0/C1/CA/D0 based on parsed page mask, log-page version UUID index, PCI ID, and capability bits. SN861 has special C0 handling and skips older CA flow.
- OCP log wrappers are thin capability checks around low-level getters that validate log versions and GUIDs.
- Drive status and assert clear depend on C2 Device Manageability entries for assert, thermal, EOL, and format-corrupt state.
- Drive Essentials creates a timestamped directory, saves identify/log/feature/VU-file/dumptrace data, then archives it via a constructed `tar` command.
- Enclosure logs use either NIC get-log-page chunking or send/receive management passthrough loops.
- `wdc_set_latency_monitor_feature()` packs CLI threshold fields into `struct feature_latency_monitor` and calls `nvme_set_features()` for `NVME_FEAT_OCP_LATENCY_MONITOR`.

## State, Data, and Dependencies

- State is mostly transient heap/stack buffers, with persistent side effects from output files, Drive Essentials archives, reason-id files, and device mutations from clear/resize/feature-setting commands.
- Depends heavily on libnvme identify/get-log/get-feature/set-feature/admin passthrough APIs, nvme-cli argument/output helpers, JSON helpers, endian conversion, WDC/OCP constants, GUID arrays, device IDs, capability masks, and print utilities.
- Cross-chunk dependencies from earlier lines include `wdc_check_device()`, `wdc_get_drive_capabilities()`, `wdc_get_pci_ids()`, `wdc_nvme_check_supported_log_page()`, UUID/C2 helpers, print helpers, data tables, and constants.
- Command registration likely lives outside this chunk and calls the final `run_wdc_*` wrappers.

## Risks and Edge Cases

- Device-provided payload bounds are weak in several paths: C1 subpage walking, C2/VU directory offsets, and Drive Essentials file sizes.
- Several parsers cast raw byte buffers directly to structs; this is layout, alignment, and endian sensitive.
- NAND stats uses `__u64 *` casts into byte arrays for normalized/raw fields, risking unaligned access.
- `wdc_de_get_dump_trace()` appears suspicious: it mixes dword offsets with byte pointer arithmetic and passes `offsetInDwords` as `0` for every chunk.
- `wdc_do_drive_essentials()` builds a shell command with `system()` using user/device-derived path components without shell quoting.
- `wdc_enc_get_log()` opens an output file but does not explicitly close it in this chunk.
- Output format handling is inconsistent: many command-local configs hardcode `"normal"` while some paths use global `nvme_args.output_format`.
- Mutating commands act after capability checks with minimal confirmation: resize, clear counters/history/assert, telemetry option, and latency monitor feature.
- `wdc_enc_get_nic_log()` writes the full requested dump length even after a chunk read failure.
- `stringify_log_page_guid()` uses `%x` instead of zero-padded `%02x`, so GUID strings can lose leading zero nibbles.

## Cross-Chunk References

- This chunk starts inside `wdc_get_ca_log_page()`; setup and earlier switch cases are in the previous chunk.
- Most structure definitions, constants, GUIDs, capability calculations, and print helpers are defined before this chunk.
- The final `run_wdc_*` wrappers are the bridge from these implementations to plugin registration outside this line range.
- `wdc_set_latency_monitor_feature()` is non-static and also exposed through `run_wdc_set_latency_monitor_feature()`.
