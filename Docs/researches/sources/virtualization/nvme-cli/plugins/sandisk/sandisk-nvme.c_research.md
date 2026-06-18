# File Research: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-nvme.c

## Role

`sandisk-nvme.c` is the implementation file for the Sandisk nvme-cli plugin. It registers command handlers through `sandisk-nvme.h`, implements Sandisk-specific telemetry/internal log paths, SN861 resize, firmware activation history on C2 logs, clear firmware history via vendor feature, capability reporting, and delegates many commands to the WDC plugin compatibility layer.

The plugin version in the header is `3.1.3`, and this source pulls in `plugins/wdc/wdc-nvme-cmds.h` because most command handlers are wrappers around `run_wdc_*` functions.

## Telemetry and Internal Firmware Log Capture

The largest command path is `sndk_vs_internal_fw_log()`. It parses options for output file, transfer size, data area, telemetry type, verbose mode, and deprecated file-size/offset parameters. It opens the NVMe handle, scans topology, checks that the device is Sandisk/WDC-supported, builds a default output filename from the controller serial and timestamp when none is provided, validates data-area values, parses the requested telemetry type (`NONE`, `HOST`, `CONTROLLER`, or `BOTH`), obtains device capabilities, and selects the capture method.

`sndk_do_cap_telemetry_log()` captures NVMe telemetry logs through libnvme. It validates telemetry support via controller `lpa`, optionally enables ETDAS for data area 4, handles host-initiated versus controller-initiated selection, rejects `BOTH`, opens the output file, retrieves the full telemetry log through libnvme, writes the full buffer, fsyncs it, clears ETDAS if it changed host behavior, and frees the log.

`sndk_do_cap_both_telemetry_log()` captures host and controller telemetry separately into temporary files, then packages them into a tar file by constructing and executing a `tar -cf` command. It removes the temporary files afterward.

`sndk_do_cap_udui()` captures Device Unit Info through vendor opcode `0xFA`, first reading an NVMe telemetry-like header to determine total size from `dalb4`, then reading chunks by offset via `sndk_dump_udui_data()` and writing them to the output file.

If Sandisk-specific capabilities are not present, `sndk_vs_internal_fw_log()` falls back to `run_wdc_vs_internal_fw_log()`.

## Resize Command

The file defines an SN861-specific resize admin command:

- opcode `0xD1`
- 4096-byte buffer
- `cdw10 = 0x40`
- `cdw12 = 0x103`
- `cdw13 = 0x1`
- new size copied into the command buffer

`sndk_drive_resize()` checks capabilities and uses this path when `SNDK_DRIVE_CAP_RESIZE_SN861` is set. Otherwise, it delegates to `run_wdc_drive_resize()`.

## Firmware Activation History

The file has a C2 log GUID constant `ocp_C2_guid` and C2 firmware activation history support:

- `sndk_get_fw_act_history_C2()` reads log page `0xC2`, validates the log page GUID, limits entries to `SNDK_MAX_NUM_ACT_HIST_ENTRIES`, and dispatches printing.
- `sndk_print_fw_act_history_log_normal()` prints a tabular text view of entry number, timestamp, power-cycle count, previous/new firmware, slot, action bits, and result.
- `sndk_print_fw_act_history_log_json()` prints one JSON object per entry.
- `sndk_print_fw_act_history_log()` selects normal or JSON output.

Both normal and JSON paths detect the oldest entry when the circular table is full by comparing adjacent firmware activation history entry numbers.

`sndk_clear_fw_activate_history()` uses `sndk_do_clear_fw_activate_history_fid()` when the drive supports `SNDK_DRIVE_CAP_VU_FID_CLEAR_FW_ACT_HISTORY`; that helper sets feature ID `0xC1` with bit 31 set. Otherwise, the command delegates to WDC.

## Delegated Command Wrappers

Many handlers are thin wrappers to WDC plugin commands:

- NAND stats
- additional SMART log
- clear PCIe correctable errors
- drive status
- clear assert dump
- telemetry controller option
- reason identifier
- log page directory
- namespace resize
- drive info
- cloud SSD plugin version
- PCIe stats
- latency monitor log
- error recovery log
- device capabilities log
- unsupported requests log
- cloud boot SSD version
- cloud log
- hardware revision log
- device WAF
- set latency monitor feature
- temperature stats
- customer unique SMART log

This file therefore acts as a compatibility facade: Sandisk-specific capability detection decides whether to run local logic or reuse the WDC implementation.

## Capabilities Command

`sndk_capabilities()` scans topology, validates the device, retrieves the capability bitmask via `sndk_get_drive_capabilities()`, and prints a supported/not-supported line for each user-facing command and several underlying log pages. It reports `capabilities` itself as always supported after reaching that point.

## Dependencies and Integration

The file depends on libnvme, nvme-cli command parsing (`NVME_ARGS`, `parse_and_open`), cleanup attributes, `sandisk-utils.h`, and WDC command shims. It is compiled with `CREATE_CMD` before including `sandisk-nvme.h`, which causes the plugin command table to bind to the static functions defined here.

## Notable Risks

`sndk_do_cap_both_telemetry_log()` uses `system()` with a shell command assembled from file paths, quoting with double quotes but not escaping embedded double quotes or shell metacharacters inside paths. The telemetry capture path uses blocking writes and full-buffer allocation. Several local variables such as `device_id` and `read_vendor_id` are retrieved but not used in `sndk_vs_internal_fw_log()`. The JSON firmware-history printer reuses a single JSON root object across entries, which relies on overwriting identical keys before each print rather than creating a fresh object per entry.
