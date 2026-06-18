# File Research: sources/virtualization/nvme-cli/nvme-print-json.c

## Purpose

`nvme-print-json.c` is the JSON output backend for `nvme-cli`. It implements a large `struct print_ops` table and maps nvme-cli/libnvme print callbacks into JSON object construction using `util/json.h`. The file is not command execution logic; it is presentation logic for NVMe identify data, log pages, feature decoders, topology views, status/error reporting, and raw buffer dumps.

## Main Entry Points

- `nvme_get_json_print_ops(nvme_print_flags_t flags)` returns the JSON `print_ops` implementation after storing the active output flags.
- `json_print(struct json_object *r)` serializes a JSON object, prints a newline, and frees the object.
- `json_show_init()` / `json_show_finish()` support grouped JSON output through the file-global `json_r` object and nested `json_init` counter.
- `json_output_status()`, `json_output_opcode_status()`, `json_output_error_status()`, `json_output_message()`, `json_output_perror()`, and `json_output_key_value()` provide JSON-formatted command status and message output.

## Structure And Responsibilities

The file starts with JSON helper aliases and wrappers:

- `obj_add_*` aliases wrap the project JSON helpers.
- `d_json()` and `obj_d()` convert binary buffers into arrays of printable ASCII rows.
- `obj_add_result()` and `obj_add_key()` format variadic text into JSON fields.
- `obj_create()` changes behavior depending on whether grouped output is active: standalone calls create and print a single object, while grouped calls add a new array/object under `json_r`.

The central mode switch is `verbose_mode()`, which tests `json_print_ops.flags & VERBOSE`. Many callbacks emit raw numeric fields in normal mode and decoded, human-readable sub-objects in verbose mode.

## NVMe Identify Formatting

The file formats multiple identify structures:

- `json_nvme_id_ctrl()` emits controller identify data, including serial/model/firmware strings, power state descriptors, capabilities, namespace counts, command set attributes, fabrics fields, and optional vendor-specific data callback output.
- `json_nvme_id_ns()` emits namespace capacity/usage, feature bits, protection and metadata fields, LBA formats, NGUID/EUI64, and vendor-specific bytes.
- `json_nvme_id_ns_lbaf()` formats namespace LBA formats, using verbose descriptions when requested.
- `json_id_iocs()` and `json_id_iocs_iocsc()` format I/O command set combinations.
- `json_nvme_cmd_set_independent_id_ns()`, `json_nvme_id_ctrl_nvm()`, `json_nvme_nvm_id_ns()`, `json_nvme_zns_id_ctrl()`, and `json_nvme_zns_id_ns()` cover command-set-specific identify data for independent, NVM, and ZNS structures.
- `json_nvme_id_ns_descs()` parses namespace identifier descriptor records and emits EUI64, NGUID, UUID, and CSI descriptors.
- `json_nvme_id_uuid_list()`, `json_id_domain_list()`, `json_nvme_id_nvmset()`, `json_nvme_endurance_group_list()`, `json_nvme_list_ns()`, and `json_nvme_list_ctrl()` format list-style identify responses.

## Log Page Formatting

The file contains JSON formatters for a wide range of NVMe log pages:

- Health and reliability: `json_smart_log()`, `json_endurance_log()`, `json_error_log()`, `json_self_test_log()`, `json_sanitize_log()`.
- Namespace and ANA state: `json_changed_ns_list_log()`, `json_ana_log()`, `json_lba_status()`, `json_lba_status_log()`, `json_resv_notif_log()`, `json_nvme_resv_report()`.
- Capability/effects: `json_effects_log()`, `json_effects_log_list()`, `json_fid_support_effects_log()`, `json_mi_cmd_support_effects_log()`, `json_support_log()`.
- FDP and placement: `json_nvme_fdp_configs()`, `json_nvme_fdp_usage()`, `json_nvme_fdp_stats()`, `json_nvme_fdp_events()`, `json_nvme_fdp_ruh_status()`.
- Persistent events: `nvme_json_pevent_log_head()`, `json_pevent_entry()`, and per-event helpers for SMART, firmware commit, timestamp, power-on reset, namespace changes, format, sanitize, set-feature, telemetry, thermal excursion, and vendor-specific event data.
- Physical/media logs: `json_phy_rx_eom_log()`, `json_phy_rx_eom_descs()`, `json_media_unit_stat_log()`, `json_supported_cap_config_log()`, `json_rotational_media_info_log()`, `json_power_meas_log()`.
- Fabrics/discovery logs under `CONFIG_FABRICS`: discovery, host discovery, and AVE discovery formatting.

## Register And Property Formatting

The register code has two layers:

- Field decoders such as `json_registers_cap()`, `json_registers_cc()`, `json_registers_csts()`, `json_registers_cmbloc()`, `json_registers_cmbsz()`, `json_registers_pmrcap()`, and related PMR/CMB/boot partition helpers.
- MMIO readers such as `json_ctrl_registers_cap()` through `json_ctrl_registers_pmrmscu()` that read BAR offsets and either emit raw numbers or verbose decoded objects.

`json_ctrl_registers()` emits the full controller register set. `json_ctrl_register()` handles a single register value. `json_single_property()` handles NVMe property output, using `json_single_property_human()` in verbose mode.

## Feature Formatting

Feature output is organized around `json_feature_show()` and `json_feature_show_fields()`.

`json_feature_show()` prints the feature ID, name, selected value, and either supported/select information or decoded fields. `json_feature_show_fields()` dispatches by feature ID to specific decoders for arbitration, power management, LBA ranges, temperature thresholds, error recovery, volatile write cache, queue counts, interrupt coalescing/configuration, async events, APST, host memory buffer, timestamp, KATO, HCTM, NOPSC, read recovery level, predictable latency, host behavior, sanitize, endurance event config, IOCS profile, spinup, power loss signaling, performance characteristics, metadata, host ID, reservations, write protection, FDP, boot partition write protection, power limit, power threshold, and power measurement.

The feature decoders mostly transform packed bitfields into named JSON keys while preserving some raw values.

## Topology And List Output

The file also implements JSON output for libnvme topology/list commands:

- `json_print_nvme_subsystem_list()` emits hosts, subsystems, controllers/paths, ANA state, and optional verbose subsystem metadata.
- `json_detail_list()` and `json_detail_list_v2()` emit detailed host/subsystem/controller/namespace trees.
- `json_simple_list()` emits a flat `Devices` array of namespace device paths and size data.
- `json_simple_topology()` emits host/subsystem/namespace topology with controller/path data.
- Multipath helpers add path ANA state, I/O policy-dependent fields, controller state, transport, and address details.
- `obj_add_ctrl_address_details()` centralizes optional transport address details such as `traddr`, `host_traddr`, `host_iface`, and `trsvcid`.

## Print Ops Registration

The `json_print_ops` table binds almost all JSON formatters to the generic nvme-cli print interface. This includes libnvme data printers, topology/list printers, and message/status printers. Any command using this `print_ops` backend gets JSON behavior through that table rather than calling these functions directly.

## Notable Implementation Details

- Endianness is consistently converted with `le*_to_cpu()` before JSON emission.
- 128-bit NVMe counters use `le128_to_cpu()` and `obj_add_uint128()`.
- Some binary data is emitted as printable ASCII rows rather than hex bytes.
- Several functions allocate temporary formatted strings with `asprintf()`/`vasprintf()` and rely on `__cleanup_free`.
- The persistent event parser bounds-checks event offsets against the supplied size before decoding entries.
- Fabrics-specific formatters compile to empty stubs when `CONFIG_FABRICS` is disabled.
- `json_pull_model_ddc_req_log()` contains a direct `printf("tpdrpl: %u\n", tpdrpl);` before adding JSON fields, which appears inconsistent with pure JSON output and is worth checking if strict JSON output matters.

## Dependencies

This file depends on:

- `libnvme.h` for NVMe structures, topology handles, status helpers, register helpers, and fabrics helpers.
- `nvme-print.h` for `struct print_ops` and print flags.
- `util/json.h` for JSON object construction and serialization.
- `nvme.h`, `common.h`, and `logging.h` for shared helpers, command globals, constants, and error strings.
- Conditional `CONFIG_FABRICS` and `CONFIG_MI` blocks for fabrics and NVMe-MI output paths.

## Risks And Maintenance Notes

- The file is very broad and mirrors NVMe specification growth. Adding new log pages or features requires updating both a formatter and the `json_print_ops` table.
- JSON key naming is not fully uniform; some keys are raw field names, some are human-readable spec descriptions, and some include spaces or punctuation. Downstream consumers may depend on these exact names.
- Verbose and non-verbose output schemas often differ structurally, so consumers should not assume stable shape across flags.
- Several parsers walk variable-length device-provided buffers. Existing checks are present in some paths, but new additions should be careful about length validation before pointer arithmetic.
- `json_r`/`json_init` is global state. It is suitable for the current CLI print model, but not reentrant.
