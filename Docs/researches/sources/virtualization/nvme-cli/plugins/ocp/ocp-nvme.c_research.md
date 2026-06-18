# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-nvme.c

## Role

`ocp-nvme.c` is the main implementation file for the `nvme-cli` OCP cloud SSD plugin. It registers and implements user-facing commands for OCP log pages, vendor-specific feature get/set operations, telemetry retrieval/parsing, persistent event log decoding, and several delegated OCP helper commands.

The source tree `sources/virtualization/nvme-cli` is included by `Docs/research_subset_a.md`, so this file is in subset A scope.

## Command Surface

Through `CREATE_CMD` plus `ocp-nvme.h`, this file provides handlers for:

- log retrieval: latency monitor C3, unsupported requirements C5, error recovery C1, device capabilities C4, telemetry string C9, TCG configuration C7, persistent event log, hardware component log, firmware activation history, and SMART extended log through a wrapper;
- mutating feature commands: latency monitor, EOL/PLP failure mode, DSSD power state, PLP health check interval, telemetry profile, DSSD asynchronous event config, error injection, and IEEE1667 silo;
- feature readers: latency monitor, clear PCIe correctable errors, DSSD power state, PLP health interval, telemetry profile, DSSD async event config, error injection, IEEE1667 silo, and idle wake-up time configuration;
- telemetry workflows under `internal-log`, including fetching device telemetry/string binaries or parsing user-provided binaries.

## Core Data Flow

Most command handlers follow the same pattern: define CLI option metadata with `NVME_ARGS`, call `parse_and_open()` to obtain a libnvme transport handle, validate output format when needed, call libnvme `get_log`, `get_features`, `set_features`, or admin passthrough APIs, then dispatch decoded output through `ocp-print.c` wrappers.

For fixed OCP log pages, helpers allocate a buffer, call `ocp_get_log_simple()` or a tailored `nvme_init_get_log()` path, verify the OCP log page GUID byte-for-byte, cast the buffer to the packed wire-layout struct from `ocp-nvme.h`, and pass it to the selected printer. This pattern is used for C3 latency monitor, C5 unsupported requirements, C1 error recovery, C4 device capabilities, and C7 TCG configuration.

Feature commands commonly use `ocp_get_uuid_index()` unless the user passes `--no-uuid`, reflecting OCP 2.0 UUID-index requirements. Some commands intentionally use NSID zero, `NVME_NSID_NONE`, or `NVME_NSID_ALL` according to OCP version notes and feature semantics.

## Telemetry Behavior

The telemetry section is the largest subsystem in the file. It can:

- fetch host/controller telemetry headers and data areas with admin passthrough;
- save telemetry and C9 string logs to binary files;
- parse telemetry and string binaries through `parse_ocp_telemetry_log()`;
- print telemetry headers, data area 1 metadata, statistics descriptors, and event FIFOs;
- handle data area 4 by setting and later clearing ETDAS through libnvme helpers;
- retrieve C9 telemetry string log data, compute dynamic table offsets/sizes, optionally save binary output, and route decoded output through `ocp_c9_log()`.

Global buffers such as `header_data`, `log_data`, `ptelemetry_buffer`, `pstring_buffer`, and `pC9_string_buffer` are used across telemetry helper calls. This makes the telemetry path stateful within the process and couples retrieval with later print dispatch.

## Persistent Event Log

`ocp_get_persistent_event_log()` extends standard NVMe persistent event log retrieval with OCP-aware printing. It first reads the log header, determines the total length or handles establish/release context actions, allocates huge memory for the full log, re-reads the header to compare generation numbers, and then calls `ocp_show_persistent_event_log()`.

The printer can later identify OCP TCG activity vendor-specific events through `ocp_is_tcg_activity_event()` and decode the OCP `tcg_activity_event_data` layout declared in `ocp-nvme.h`.

## Dependencies

Important dependencies include libnvme transport, identify, get-log, get-feature, set-feature, admin passthrough, persistent event log, UUID-index, and ETDAS APIs; nvme-cli argument parsing and print helpers; OCP-specific helpers from `ocp-utils.h`; telemetry decoding from `ocp-telemetry-decode.h`; hardware component, firmware activation history, clear-feature, and SMART modules; POSIX file I/O for binary telemetry/string dumps.

## Notable Risks And Edge Cases

- Several paths trust device-reported table sizes and offsets when allocating variable-length arrays or copying dynamic telemetry/string-log tables.
- Some allocated telemetry buffers are not freed on all early error paths, especially within repeated data-area FIFO/stat processing.
- `extract_dump_get_log()` opens its output file only inside the non-final chunk branch; very small one-chunk dumps risk writing to an invalid descriptor.
- `get_telemetry_data()` shifts the high 32 bits of `offset` by 8 when filling `cdw13`, which is unusual for a 64-bit log page offset split.
- Error reporting is inconsistent: some commands use `nvme_show_error()`, some use `fprintf()`, and some print success/status even when JSON output was requested.
- Binary and normal/json paths are not equally supported for every command; some command-local configs hardcode `"normal"` despite global output-format support.
- Mutating commands perform device changes without confirmation, so command-line parsing and UUID/NSID selection are the primary safety gates.
