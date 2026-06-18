# File Research: sources/virtualization/nvme-cli/plugins/micron/micron-nvme.c

## Role

Large Micron nvme-cli plugin implementation. It implements Micron vendor commands, OCP-like Micron log decoders, debug log package collection, feature controls, firmware update/history helpers, SMART/health extensions, and Identify Controller vendor-field display.

The file is compiled as an nvme-cli plugin translation unit by defining `CREATE_CMD` and including `micron-nvme.h`, which registers the command table.

## Command Surface Implemented

Registered via `micron-nvme.h` and implemented here:

- `select-download`: selective firmware download and commit for older 9200-style flows.
- `vs-temperature-stats`: SMART temperature and sensors.
- `vs-pcie-stats`: PCIe error status/counters through Micron admin command or `setpci`.
- `clear-pcie-correctable-errors`: clears PCIe correctable errors via Micron feature/admin command or `setpci`.
- `vs-internal-log`: builds Micron debug package from controller, namespace, SMART, error, telemetry, feature, and vendor logs.
- `vs-telemetry-controller-option`: toggles controller telemetry generation feature.
- `vs-nand-stats`: Micron/OCP NAND health statistics.
- `vs-smart-ext-log`: extended SMART pages.
- `vs-drive-info`: hardware/FTL/boot-spec/ownership fields.
- `plugin-version` and `cloud-SSD-plugin-version`.
- `log-page-directory`: probes supported log pages.
- `vs-fw-activate-history`: parses Micron firmware activation history.
- `latency-tracking`, `latency-stats`, `latency-logs`: latency monitor feature/log controls.
- `vs-smart-add-log`: OCP-style additional SMART log.
- `clear-fw-activate-history`: clear firmware activation history.
- `vs-smbus-option`: SMBus feature toggle/status.
- `cloud-boot-SSD-version`, `vs-device-waf`, `vs-cloud-log`.
- `vs-work-load-log`, `vs-vendor-telemetry-log`.
- `smart-log`: Micron SMART/health output.
- `id-ctrl`: Identify Controller with Micron vendor fields.

## Drive Model Detection

The file defines `enum eDriveModel` with `M5410`, `M51AX`, `M51BX`, `M51BY`, `M51CY`, `M51CX`, `M5407`, `M5411`, `M6001`, `M6003`, `M6004`, and `UNKNOWN_MODEL`.

`GetDriveModel()` reads sysfs vendor/device IDs from:

- `/sys/class/nvme/nvme%d/device/vendor`
- `/sys/class/misc/nvme%d/device/vendor`
- `/sys/class/nvme/nvme%d/device/device`
- `/sys/class/misc/nvme%d/device/device`

It requires Micron vendor ID `0x1344`, then maps PCI device IDs to the internal model enum. Many command handlers gate behavior by this enum.

## Core Helpers

- `WriteData()` appends binary log data to a file under a directory.
- `ReadSysFile()` reads hex sysfs IDs.
- `ZipAndRemoveDir()` packages a generated debug directory using `tar -zcf` for `.tgz`/`.tar.gz`, otherwise `zip -r`, then deletes the temporary directory.
- `SetupDebugDataDirectories()` validates output path context, normalizes serial number text into a directory name, creates main/`OS`/`Controller` directories, and handles collisions by suffixing `-N`.
- `GetLogPageSize()` reads common log headers for log IDs `0xC1`, `0xC2`, `0xC4`.
- `NVMEGetLogPage()` manually builds Get Log Page admin passthroughs, handling chunking, offsets, and special cases for telemetry/log IDs `0x07`, `0x08`, `0xE6`, `0xE7`, `0xE9`.
- `NVMEResetLog()` repeatedly reads a log until `0xdeadbeef` or max size.
- `GetCommonLogPage()` allocates and fetches a log with `nvme_get_log_simple()`.
- `micron_parse_options()` wraps `parse_and_open()` and optional model detection.

## Firmware Download and Commit

`micron_selective_download()` parses `--fw` and `--select`, accepts select strings `OOB`, `EEP`, and `ALL`, reads the firmware image, validates DWORD alignment, downloads in 4096-byte chunks using `nvme_init_fw_download()`, then commits through `micron_fw_commit()`. Commit status `0x10B` or `0x20B` is treated as a successful update requiring power cycle.

## Feature Controls

Micron vendor feature IDs include:

- `0xC3`: clear PCI correctable errors.
- `0xC1`: clear firmware activation history.
- `0xCF`: telemetry control option.
- `0xD5`: SMBus option.
- `0x16`: OCP enhanced telemetry.

`micron_smbus_option()` supports `enable`, `disable`, and `status` for selected models, using `nvme_set_features_simple()` and `nvme_get_features()`.

`micron_telemetry_cntrl_option()` validates telemetry support through `ctrl.lpa & 0x8`, then enables, disables, or reads feature `0xCF`.

`micron_clr_fw_activation_history()` uses feature `0xC1` with bit 31 set for M51CX/M51BY/M51CY/M6003/M6004.

## Temperature and PCIe Statistics

`micron_temp_stats()` reads `nvme_smart_log`, emits normal or JSON output. The composite temperature is decoded from Kelvin to Celsius.

Implementation note: sensor loop condition uses `tempSensors[i]` before assigning from `smart_log.temp_sensor[i]`, so sensor reporting appears unreachable with zero-initialized `tempSensors`.

`micron_pcie_stats()` supports:

- M5407 vendor admin command `0xD6` for counter retrieval.
- Fallback sysfs path lookup and `setpci` reads of AER correctable/uncorrectable registers.
- JSON or normal formatting through `pcie_correctable_errors[]` and `pcie_uncorrectable_errors[]`.

`micron_clear_pcie_correctable_errors()` clears through feature `0xC3` for M51CX/M51BY/M51CY, admin opcode `0xD6` for M5407, or fallback `setpci` write to AER correctable error status.

## SMART, NAND, and Vendor Log Decoding

The file defines several `struct request_data` tables describing binary log layouts:

- `ocp_c0_log_page`: OCP SMART Cloud Health Log for M51CX.
- `hyperscale_c0_log_page`: Hyperscale NVMe Boot SSD extended health.
- `datacenter_c0_log_page`: datacenter NVMe SSD SMART layout for M51BY/M51CY.
- `e1_log_page`: extended SMART.
- `fb_log_page`: vendor-specific health log.
- `D0_log_page`: Nitro `0x6001` extended health.
- `C5_log_page`: Micron workload log.
- `C6_log_page`: vendor telemetry log.

Output uses `generic_structure_parser()` for many layouts and custom helpers for D0 and hyperscale NAND stats.

`micron_nand_stats()` identifies the model, reads controller data, handles Hyperscale GG customer ID on M51CX through `0xC0`, otherwise reads `0xD0` and optionally `0xFB`.

`micron_smart_ext_log()` selects `0xE1` for M51CX/M51BY/M51CY/M6003/M6004 and `0xD0` for M6001.

`micron_work_load_log()` and `micron_vendor_telemetry_log()` read `0xC5` and `0xC6` for M6001/M6003/M6004.

`micron_ocp_smart_health_logs()` prints `0xFB` for M5410/M5407 or `0xC0` for M51CX/M51BY/M51CY/M6003/M6004.

## Debug Package Collection

`micron_internal_logs()` is the largest workflow:

1. Parses package path and optional telemetry-only mode.
2. Opens device, identifies model and controller.
3. For telemetry-only mode, reads host/controller telemetry data area and writes directly to the requested package file.
4. For package mode, creates serial-number-based temp directories.
5. Writes timestamp, controller identify data, OS config snapshots, drive info, namespace identify data, SMART, error, generic logs, telemetry, feature settings, and vendor logs.
6. Selects vendor log lists based on model families.
7. Fetches logs with model-specific handling for common-log wrapped pages, telemetry pages, resettable logs, and chunked logs.
8. Archives the directory and removes temporary data.

It calls shell commands for OS information (`uname`, `lsmod`, `/proc/*`, `dmesg`) and packaging (`zip`, `tar`, `rm`), so runtime behavior depends on host tools and permissions.

## Telemetry Logic

`micron_telemetry_log()` reads telemetry header, calculates data area sizes, reallocates to the selected area size, then reads the requested host/controller telemetry data.

`GetOcpEnhancedTelemetryLog()` enables ETDAS through feature `0x16`, reads telemetry header and data areas 1-4, and appends host/controller telemetry log data to package files.

## Firmware Activation History

The file has Micron-specific packed structures:

- `fw_activation_history_entry`
- `micron_fw_activation_history_table`

`micron_fw_activation_history()` reads log `0xC2`, validates page ID and version, checks entry count, then prints normal table output or JSON. `display_fw_activate_entry()` formats power-on time, power cycle count, previous/new firmware, slot, commit action, and result.

## Latency Monitor

Feature/log IDs:

- Feature `0xD0`: latency monitor.
- Log `0xD1`: latency monitor entries.
- Log `0xD0`: bucketed command latency stats.

`micron_latency_stats_track()` enables/disables/statuses latency tracking by command mask (`read`, `write`, `trim`, `all`) and validates threshold in 10ms units.

`micron_latency_stats_logs()` prints 16 command-level latency log entries as CSV-like output.

`micron_latency_stats_info()` prints latency bucket histograms for all/read/write/trim.

## Health and Identify Extensions

`micron_health_info()` reads standard SMART/Health log and prints Micron-oriented normal or JSON output. It exposes standard counters plus Micron-specific `op_lifetime_energy_consumed` and `interval_power_measurement`.

`micron_id_ctrl()` calls `nvme_show_id_ctrl()` with `micron_id_ctrl_vs()` to display Micron vendor fields derived from controller structure fields:

- `pms`: bit 21 of `ctratt`.
- `ipmsr`.
- `msmt`.

## External Dependencies

This file depends heavily on nvme-cli/libnvme APIs:

- `parse_and_open()`, `argconfig`, `NVME_ARGS`.
- `libnvme_exec_admin_passthru()`, `libnvme_get_log()`.
- `nvme_get_log_simple()`, `nvme_get_log_smart()`, `nvme_identify_ctrl()`, `nvme_identify_ns()`.
- `nvme_get_features()`, `nvme_set_features()`, `nvme_set_features_simple()`.
- `generic_structure_parser()`, JSON helpers, output-format validation.
- cleanup attributes from `util/cleanup.h`.

It also depends on Linux `/sys`, `/proc`, `/dev/nvme*`, and external commands `setpci`, `zip`, `tar`, `gzip`, `rm`, and common shell utilities.

## Important Implementation Notes

- Many paths use `sprintf()` into fixed buffers; inputs are largely device paths or package paths.
- Several commands rely on `argv[optind]` being a device path after parsing.
- The debug package path logic validates parent directory only when a slash is present.
- The file mixes standard nvme-cli APIs with raw admin passthroughs.
- Some device-model checks return success even when unsupported options are printed, preserving nvme-cli plugin convention in parts of the file.
- The code assumes Linux sysfs layout and will not be portable outside that environment.
