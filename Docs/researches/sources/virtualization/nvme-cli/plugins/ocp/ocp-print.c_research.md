# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-print.c

## Role

`ocp-print.c` is the output dispatch layer for the OCP plugin. It chooses a print backend based on nvme-cli output flags and exposes one wrapper function per OCP log type.

## Dispatch Model

`ocp_print_ops()` selects:

- JSON ops when the passed flags include `JSON` or the global nvme-cli output format is JSON;
- binary ops when flags include `BINARY`;
- stdout ops otherwise.

The `ocp_print()` macro retrieves the backend, checks that the requested callback exists, invokes it, or prints `unhandled output format` to stderr.

## Public Wrappers

The file exports wrappers declared in `ocp-print.h`:

- `ocp_show_hwcomp_log()`
- `ocp_fw_act_history()`
- `ocp_show_persistent_event_log()`
- `ocp_smart_extended_log()`
- `ocp_show_telemetry_log()`
- `ocp_c3_log()`
- `ocp_c5_log()`
- `ocp_c1_log()`
- `ocp_c4_log()`
- `ocp_c9_log()`
- `ocp_c7_log()`

These wrappers keep command code independent from concrete formatting implementations.

## Dependencies

The dispatch layer depends on `nvme-print.h` for output flags and global format detection, `ocp-print.h` for the vtable, and OCP log type declarations.

## Notable Risks And Edge Cases

- Backend selection gives JSON precedence over binary if JSON is globally configured, even if call-site flags are ambiguous.
- Missing backend callbacks are reported only as a generic runtime message, not as command-specific validation failures.
- Backend objects are static and mutate their `flags` field on each `ocp_get_*_print_ops()` call, which is simple for a CLI process but not reentrant state.
