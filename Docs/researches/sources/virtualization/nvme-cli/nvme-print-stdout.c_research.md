# File Research: sources/virtualization/nvme-cli/nvme-print-stdout.c

## Role In The Source Tree

`nvme-print-stdout.c` implements the plain text/stdout backend for nvme-cli output. It is the human-readable and classic CLI renderer behind a `struct print_ops` vtable. Command code elsewhere gathers NVMe data through libnvme and kernel/device ioctls; this file turns those typed NVMe structures into stdout/stderr text, tables, topology trees, hexdumps, and verbose bitfield explanations.

The file is large because it covers most NVMe administrative surfaces: identify data, controller registers, log pages, features, ZNS, FDP, fabrics discovery, reservations, sanitize, SMART/health, command effects, topology, and generic list output.

## Main Dependencies

The file depends heavily on:

- `libnvme.h` for NVMe structs, endian conversion helpers, status helpers, string conversion helpers, topology iterators, and fabrics definitions.
- `nvme-print.h` for the `print_ops` interface and print flags such as `VERBOSE` and `VS`.
- `util/table.h` for aligned tabular output.
- `util/suffix.h` for SI/binary size formatting.
- CCAN `strset` and typed htables for deduplicating topology resources.
- `logging.h` and `common.h` for diagnostics and shared helpers.
- `CONFIG_FABRICS` and `CONFIG_MI` conditionals for fabrics and NVMe-MI-specific printing.

Almost all data read from devices is treated as little-endian NVMe-defined binary and converted at print time with `le16_to_cpu`, `le32_to_cpu`, `le64_to_cpu`, `le128_to_cpu`, or helper accessors.

## Print Backend Registration

The core export is:

- `nvme_get_stdout_print_ops(nvme_print_flags_t flags)`

It stores the requested flags into the static `stdout_print_ops` object and returns a pointer to it. The vtable at the end maps high-level print operations to local functions, including:

- Identify: `.id_ctrl`, `.id_ns`, `.id_ctrl_nvm`, `.nvm_id_ns`, `.zns_id_ctrl`, `.zns_id_ns`, `.id_ns_descs`, `.id_uuid_list`, `.id_iocs`, `.id_domain_list`.
- Logs: `.smart_log`, `.error_log`, `.fw_log`, `.ana_log`, `.sanitize_log_page`, `.persistent_event_log`, `.supported_log_pages`, `.power_meas_log`, FDP logs, reachability logs, fabrics logs.
- Topology/listing: `.list_items`, `.print_nvme_subsystem_list`, `.topology_ctrl`, `.topology_namespace`, `.topology_multipath`, `.topology_tabular`.
- Features and status: `.show_feature`, `.show_feature_fields`, `.show_status`, `.show_opcode_status`, `.show_error_status`.
- Utility output: `.d` hexdump, `.show_message`, `.show_perror`, `.show_key_value`.

This makes the file an output adapter, not an NVMe command executor.

## Resource And Topology Helpers

The file builds temporary resource indexes with `struct nvme_resources`, containing libnvme global context plus typed htables and string sets for subsystems, controllers, and namespaces.

Important functions:

- `nvme_resources_init()` walks hosts, subsystems, controllers, namespaces, and paths from the libnvme topology tree.
- `htable_ctrl_add_unique()` prevents duplicate controller entries by name.
- `htable_ns_add_unique()` prevents duplicate namespace pointers under the same name while still allowing multiple namespace objects with the same name when topology exposes them through different paths.
- `nvme_resources_free()` clears all temporary sets and htables.

This resource layer supports list and topology output without repeatedly traversing the libnvme tree.

## Device Path Formatting

The file has direct filesystem/device-node relevance in these helpers:

- `stdout_dev_full_path()` resolves namespace display paths. It preserves existing `/dev/spdk/...` paths, otherwise tries `/dev/<ns-name>`, then falls back to the raw namespace name.
- `stdout_generic_full_path()` maps block namespace names like `nvmeXnY` to generic character-device names like `/dev/ngXnY`, again preserving `/dev/spdk/...` paths when present.
- `stdout_ns_details()` uses corresponding shared helpers `nvme_dev_full_path()` and `nvme_generic_full_path()` for detailed listing output.

These helpers use `stat(2)` to avoid showing non-existent paths when a better fallback is available. This is the main place this file intersects with host filesystem namespace behavior.

## List And Topology Output

The file supports both simple and verbose listing modes.

Simple list path:

- `stdout_simple_list()` creates a table with columns `Node`, `Generic`, `SN`, `Model`, `Namespace`, `Usage`, `Format`, and `FW Rev`.
- `list_item()` computes namespace usage and format strings from libnvme namespace metadata, then fills a table row.
- `stdout_simple_ns()` iterates deduplicated namespace names from `strset`.

Detailed list path:

- `stdout_detailed_list()` prints three sections: subsystems, controllers, namespaces.
- `stdout_detailed_subsys()` prints subsystem name, subsystem NQN, and associated controllers.
- `stdout_detailed_ctrl()` prints controller identity, transport, address, slot, subsystem, and namespaces.
- `stdout_detailed_ns()` prints namespace path/usage/format plus parent controllers or multipath controllers.

Topology output supports namespace-ranked, controller-ranked, multipath-ranked, and tabular views:

- `stdout_simple_topology()` prints tree-like topology.
- `stdout_topology_tabular()` prints tables.
- `stdout_subsystem_topology_multipath()` includes ANA state and iopolicy-specific data.
- `stdout_tabular_subsystem_topology_multipath()` conditionally includes NUMA nodes or queue depth columns based on subsystem I/O policy.
- `stdout_tabular_subsystem_topology()` handles non-multipath controller-to-namespace topology.

## Identify Data Printers

The largest identify printer is `stdout_id_ctrl()`, which emits `struct nvme_id_ctrl`. It prints controller identity, capabilities, optional admin command support, power state descriptors, queue limits, namespace limits, controller memory buffer and PMR-related fields, fabrics fields, command support fields, and vendor-specific data when requested.

Verbose mode expands many bitfields through helper functions, for example:

- `stdout_id_ctrl_cmic()`
- `stdout_id_ctrl_oaes()`
- `stdout_id_ctrl_ctratt()`
- `stdout_id_ctrl_oacs()`
- `stdout_id_ctrl_lpa()`
- `stdout_id_ctrl_oncs()`
- `stdout_id_ctrl_sgls()`
- `stdout_id_ctrl_sanicap()`
- `stdout_id_ctrl_anacap()`

Namespace identify output is handled by:

- `stdout_id_ns()` for base namespace identify data and LBA formats.
- `stdout_cmd_set_independent_id_ns()` for command-set-independent namespace data.
- `stdout_id_ns_descs()` for namespace identification descriptors including EUI64, NGUID, UUID, and CSI.
- `stdout_nvm_id_ns()` for NVM command-set namespace extensions.
- `stdout_zns_id_ns()` for Zoned Namespace extension data.
- `stdout_zns_id_ctrl()` for ZNS controller identify data.

The code consistently supports compact raw-style output and verbose explanatory output from the same structures.

## Register Printers

Controller registers are printed by:

- `stdout_ctrl_registers()`
- `stdout_ctrl_register()`
- `stdout_single_property()`
- `stdout_ctrl_register_common()`
- `stdout_ctrl_register_human()`

Human-mode register decoding covers CAP, VS, CC, CSTS, AQA, ASQ, ACQ, CMBLOC, CMBSZ, BPINFO, BPRSEL, BPMBL, CMBMSC, CMBSTS, CMBEBS, CMBSWTP, NSSD, CRTO, PMRCAP, PMRCTL, PMRSTS, PMREBS, PMRSWTP, PMRMSCL, and PMRMSCU.

`stdout_ctrl_registers()` reads memory-mapped registers with `mmio_read32()` or `mmio_read64()`, skips registers unsupported for fabrics, and passes support state for dependent decoders such as CMBLOC and PMRSTS.

## Log Page Printers

`stdout_log()` is a dispatcher for generic get-log output by Log Identifier. It casts `args->log` to the appropriate NVMe log structure and invokes specialized printers. Some log IDs are intentionally left as no-op in this dispatcher because they are handled through other print paths.

Important log printers include:

- `stdout_error_log()` for error information entries and optional filtering.
- `stdout_smart_log()` for SMART/health data, temperature conversion, counters, energy, and interval power.
- `stdout_fw_log()` for firmware slot information.
- `stdout_changed_ns_list_log()` for changed namespace lists.
- `stdout_endurance_log()` and `stdout_endurance_group_event_agg_log()`.
- `stdout_ana_log()` for Asymmetric Namespace Access groups and namespace IDs.
- `stdout_lba_status_log()` and `stdout_lba_status()`.
- `stdout_supported_log()` for supported log pages.
- `stdout_sanitize_log()` for sanitize progress, state, estimates, and verbose status bits.
- `stdout_self_test_log()` and `stdout_self_test_result()`.
- `stdout_power_meas_log()` for power measurement logs and histograms.
- `stdout_mgmt_addr_list_log()`, `stdout_rotational_media_info_log()`, dispersed namespace, reachability group, and reachability association logs.

The persistent event log support is substantial:

- `stdout_persistent_event_log()` validates minimum header size, prints the header, then iterates event entries.
- `nvme_show_pel_header()` prints log metadata, device identity, RCI, and supported event bitmap.
- `nvme_show_pel_event_header()` prints per-event metadata and vendor-specific header data.
- Event-specific handlers print SMART health, firmware commit, timestamp change, power-on reset, namespace change, format start/completion, sanitize start/completion, set feature, thermal excursion, and vendor-specific events.

## FDP, ZNS, And Newer NVMe Feature Areas

Flexible Data Placement support includes:

- `stdout_fdp_configs()`
- `stdout_fdp_usage()`
- `stdout_fdp_stats()`
- `stdout_fdp_events()`
- `stdout_fdp_ruh_status()`
- FDP event feature decoding in `stdout_feature_show_fields()`.
- Persistent-event FDP feature decoding in `stdout_persistent_event_log_fdp_events()`.

Zoned Namespace support includes:

- ZNS identify controller and namespace printers.
- Changed zone log printing.
- Zone report printing through `stdout_zns_report_zones()`.
- Attribute decoding in `stdout_zns_report_zone_attributes()`.

These sections show the file tracks newer NVMe command-set-specific reporting instead of only legacy NVM identify/log data.

## Feature Printers

Feature output is centralized in:

- `stdout_feature_show()`
- `stdout_feature_show_fields()`
- `stdout_select_result()`

`stdout_feature_show()` prints the feature ID, feature name, select type, and raw result. If the selected output is “supported,” it decodes saveable/per-namespace/changeable bits. In verbose mode it expands known feature payloads and result fields.

Covered feature families include arbitration, power management, LBA ranges, temperature threshold, error recovery, volatile write cache, queue count, interrupt coalescing/config, write atomicity, async event configuration, APST, host memory buffer, timestamp, keep-alive timeout, host controlled thermal management, non-operational power state permissive mode, read recovery level, predictable latency mode, LBA status interval, host behavior, sanitize, endurance event config, I/O command set profile, spinup control, power loss signaling, performance characteristics, controller/namespace metadata, software progress, host identifier, reservation notification mask/persistence, namespace write protect, FDP, boot partition write protect, power limit, power threshold, and power measurement.

Feature payload helpers include:

- `stdout_lba_range()`
- `stdout_auto_pst()`
- `stdout_timestamp()`
- `stdout_host_mem_buffer()`
- `stdout_plm_config()`
- `stdout_feat_perfc()`
- `stdout_host_metadata()`
- `stdout_feat_host_id()`

## Fabrics-Specific Output

When `CONFIG_FABRICS` is enabled, the file prints NVMe-oF discovery and host discovery structures:

- `stdout_discovery_log()` prints discovery log entries including transport type, address family, subtype, transport requirements, port ID, service ID, subsystem NQN, transport address, flags, and transport-specific attributes for RDMA and TCP.
- `stdout_host_discovery_log()` prints host discovery log entries plus extended attributes.
- `stdout_ave_discovery_log()` prints AVE discovery entries and transport records.
- `print_traddr()` formats IPv4/IPv6 binary addresses with `inet_ntop()`.

When fabrics support is not compiled in, the same functions are stubbed to empty functions.

## Status, Error, And Utility Output

Status and message helpers include:

- `stdout_status()` for generic NVMe and NVMe-MI status decoding.
- `stdout_opcode_status()` for opcode-aware status strings.
- `stdout_error_status()` for prefixed error messages.
- `stdout_message()`, `stdout_perror()`, and `stdout_key_value()` for common UI messages.
- `stdout_connect_msg()` for fabrics connection progress.

`stdout_d()` is the shared hexdump implementation. It prints offsets, grouped hex bytes, and ASCII, and suppresses repeated equal lines unless debug logging is enabled. This is used for vendor-specific blobs, unknown binary fields, telemetry-like sections, and feature payloads when verbose decoding is not selected.

`print_array()` prints a named byte array in reverse order as uppercase hex.

## Output Style And Flags

The file uses the static `stdout_print_ops.flags` field throughout. Key behavior:

- `VERBOSE` enables human-readable bitfield decoding, expanded status text, explanatory lines, and sometimes table/detail modes.
- `VS` enables vendor-specific byte dumps for identify data where relevant.
- Compact mode usually prints stable key/value labels matching nvme-cli’s traditional plain text output.

Because the flags are stored in a static global print-ops object, callers should treat the returned ops as process-global mutable output configuration rather than independent per-call instances.

## Bounds And Defensive Behavior

The file has several defensive checks:

- Persistent event log printing refuses too-small buffers.
- Reservation report printing clamps entry count based on received byte length.
- Changed namespace lists detect the “more than max entries” sentinel.
- Namespace path rendering falls back when device nodes do not exist.
- Many optional data blocks are printed only if pointers or lengths indicate data is present.
- Unsupported fabrics functions compile to no-ops when the feature is absent.

There are also areas to handle carefully when modifying:

- Many functions trust controller-reported counts in variable-length logs and descriptors.
- Several loops rely on NVMe structure layout and externally validated buffer length.
- `stdout_host_metadata()` advances by descriptor length and assumes well-formed metadata descriptors.
- Pointer arithmetic on `void *` is used in GNU C style throughout the file.
- The physical receiver EOM descriptor loop advances the descriptor pointer after printing vendor-specific eye data; descriptor advancement should be preserved for all descriptor cases if that logic is edited.
- `stdout_subsystem_multipath()` contains an unusual self-assignment-style initializer for `ana_state`; it is effectively just obtaining the ANA state string, but the expression is easy to misread.

## Relevance To Filesystem And Storage Research

For `learn_fs` subset A, this file is relevant as user-space storage tooling around NVMe block devices. It does not implement filesystem logic, block allocation, or kernel I/O. Instead, it exposes how nvme-cli reports device identity, namespaces, controller topology, multipath relationships, zoned namespace geometry, LBA status, sanitize state, SMART health, reservations, and device-node paths.

The most filesystem-adjacent surfaces are:

- Namespace size, capacity, utilization, metadata size, and LBA format printing.
- Zoned Namespace reporting, including zone size, write pointer, zone state, capacity, and changed-zone logs.
- LBA status and deallocated/unwritten block behavior.
- Reservation reporting and notification logs.
- Device-node path mapping for block and generic NVMe devices.
- Multipath topology and ANA state display, which affect how hosts see and route access to namespace block devices.

## Summary

`nvme-print-stdout.c` is the stdout presentation layer for nvme-cli’s broad NVMe management surface. It is organized as many small decoders and renderers wired into one `print_ops` table. It performs little device logic itself; its core responsibility is faithful, endian-correct, flag-sensitive translation from libnvme/NVMe structs to stable terminal output. For storage research, it is most useful as a catalog of NVMe data structures and the human-facing semantics nvme-cli assigns to controller, namespace, log, feature, and topology fields.
