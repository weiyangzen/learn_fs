# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-nvme.h

## Role

`ocp-nvme.h` is both the OCP plugin command-registration header and the shared wire-format definition header for several OCP log pages and feature identifiers. It defines plugin name/version metadata, maps command names to implementation functions, and declares packed structures consumed by `ocp-nvme.c` and the print backends.

## Plugin Registration

The `PLUGIN()` block registers the `ocp` plugin as `OCP cloud SSD extensions` with version `3.0.0`. Its command list includes SMART extended log, latency monitor log and feature, internal telemetry log, firmware activation history and clear operation, EOL/PLP mode, PCIe correctable error clear/get, unsupported requirements, error recovery, device capabilities, DSSD power state, PLP health interval, telemetry string/profile, DSSD async event config, TCG configuration, error injection, IEEE1667 silo, hardware component log, persistent event log, and idle wake-up time feature.

The header uses the nvme-cli command-generation pattern with `CMD_INC_FILE`, `CMD_HEADER_MULTI_READ`, `CREATE_CMD`, and `define_cmd.h` integration.

## Wire Layouts

The header defines packed OCP/NVMe payload layouts:

- `ssd_latency_monitor_log` for C3 latency monitor data, including active/static bucket counters, timestamps, measured latencies, debug telemetry metadata, version, and GUID.
- `unsupported_requirement_log` for C5 unsupported requirement IDs.
- `ocp_error_recovery_log_page` for C1 panic/recovery action metadata, vendor recovery opcode/CDWs, previous panic IDs, version, and GUID.
- `ocp_device_capabilities_log_page` for C4 capability bits and DSSD power descriptors.
- `tcg_configuration_log` for C7 TCG state/counter information.
- `tcg_activity_event_data` for OCP vendor-specific persistent event log entries describing TCG activity.

It also defines OCP log identifiers (`enum ocp_dssd_log_id`) and feature identifiers (`enum ocp_dssd_feature_id`) used by the command implementation.

## Constants

Important constants include `GUID_LEN`, C3 latency conversion increments, C3 bucket count, operation index values for read/write/trim, C5 maximum unsupported requirement entries, and C1 previous panic ID array length.

## Dependencies And Consumers

This header depends on nvme-cli `cmd.h` and `common.h`. Its structures are consumed by `ocp-nvme.c`, `ocp-print-json.c`, `ocp-print-stdout.c`, and `ocp-print-binary.c`.

## Notable Risks And Edge Cases

- The packed structs are wire contracts; field offsets and reserved sizes must stay aligned with the OCP specification.
- Operation constants `READ`, `WRITE`, and `TRIM` are generic names and can collide conceptually with common I/O terminology, although they are local preprocessor symbols in this compilation unit scope.
- Documentation comments have minor spelling/label errors, but the main risk is any future spec drift causing printers and log retrieval validation to decode stale layouts.
