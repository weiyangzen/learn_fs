# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-print-stdout.c

## Role

`ocp-print-stdout.c` implements the normal human-readable output backend for OCP print operations. It formats OCP log pages as labeled text tables and delegates standard NVMe persistent event log sub-events to existing nvme-cli stdout printers.

## Supported Logs

The backend supports:

- hardware component log and component description listing/filtering;
- firmware activation history;
- SMART extended log;
- telemetry parse output through `print_ocp_telemetry_normal()` when JSONC support is compiled in;
- C3 latency monitor log;
- C5 unsupported requirements log;
- C1 error recovery log;
- C4 device capabilities log;
- C9 telemetry string log;
- C7 TCG configuration log;
- persistent event log with OCP TCG activity event decoding.

## Formatting Strategy

The file prints directly with `printf()`, using endian conversion helpers for device-reported fields. It uses helper routines such as `print_array()`, `convert_ts()`, `uint128_t_to_string()`, `util_uuid_to_string()`, `nvme_show_pel_header()`, and specific `nvme_show_pel_*()` event decoders.

C3 latency monitor output converts encoded timer/threshold/window values into minutes or milliseconds using constants from `ocp-nvme.h`, displays active and static bucket counters, timestamps, and measured latencies for read/write/trim operations, and conditionally prints debug telemetry log size for log page version 4 or later.

C9 telemetry string output prints the fixed header, all sixteen FIFO ASCII strings, optional statistics/event/VU event string table entries, and ASCII table bytes using offsets computed from the C9 header.

## Persistent Event Log Handling

`stdout_persistent_event_log()` prints the persistent event log header, then iterates event entries with basic size checks. Standard NVMe event types are routed to nvme-cli stdout helpers. Vendor-specific events are checked with `ocp_is_tcg_activity_event()`; matching events are decoded by `pel_tcg_activity_event()` into TCG command count, IDs, protocol/status, process time, and context bytes.

The `VERBOSE` flag stored in `stdout_print_ops.flags` controls whether standard persistent event helpers print human-readable detail.

## Notable Risks And Edge Cases

- C9 table arrays are variable-length stack arrays sized from device-provided log fields.
- C9 FIFO 15 output prints `fifo15[j]` as the numeric value but `fifo16[j]` as the ASCII character, likely a copy/paste bug.
- Several prints use 32-bit format/conversion for fields declared as 64-bit, such as C1 panic ID in some paths.
- The SMART output has spelling inconsistencies in labels, but the larger concern is that scripts may rely on exact text.
- `stdout_telemetry_log()` only does work under `CONFIG_JSONC`, even though this is the normal-output backend.
- The static `stdout_print_ops` stores flags globally for the backend.
