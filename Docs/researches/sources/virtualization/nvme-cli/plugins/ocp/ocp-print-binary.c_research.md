# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-print-binary.c

## Role

`ocp-print-binary.c` implements the binary output backend for selected OCP print operations. Instead of decoding fields, it emits raw log-page bytes through `d_raw()`.

## Implemented Operations

The backend supports raw output for:

- hardware component log, using the log's declared size and multiplying by dword size for version 1;
- persistent event log, using the caller-provided log length;
- C5 unsupported requirements log;
- C1 error recovery log;
- C4 device capabilities log;
- C9 telemetry string log, using the full retrieved log buffer;
- C7 TCG configuration log.

It does not implement binary callbacks for firmware activation history, SMART extended log, telemetry parse output, or C3 latency monitor log. Those callbacks are left `NULL`, so `ocp-print.c` will report an unhandled output format for those requests if binary output is selected.

## Dependencies

The file depends on `nvme-print.h` for `d_raw()`, `util/types.h` for integer conversion helpers, `ocp-print.h` for the print-ops interface, and OCP log structure headers.

## Notable Risks And Edge Cases

- Hardware component size is converted through `long double` and then passed to `d_raw()` as a byte count; unusual or corrupt device-reported sizes could produce unsafe output lengths before caller validation.
- The static `binary_print_ops` object stores the last requested flags, making this backend process-global rather than per-call state.
- Unsupported binary operations fail late through the dispatch layer rather than at option validation time.
