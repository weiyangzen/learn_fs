# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-print.h

## Role

`ocp-print.h` defines the OCP plugin print abstraction. It declares the `struct ocp_print_ops` callback table, backend factory functions, and public dispatch wrappers used by command implementation files.

## Print Operations

The callback table covers hardware component log, firmware activation history, persistent event log, SMART extended log, telemetry log, C3 latency monitor, C5 unsupported requirements, C1 error recovery, C4 device capabilities, C9 telemetry string, and C7 TCG configuration output. It also stores the selected `nvme_print_flags_t` for backend-specific behavior such as verbose persistent event output.

## Backend Factories

The header declares stdout and binary backend factories unconditionally. JSON backend support is conditional on `CONFIG_JSONC`; without JSONC, `ocp_get_json_print_ops()` is an inline stub returning `NULL`.

## Dependencies

The header includes all log-structure headers needed to type the callback signatures: hardware component, firmware activation history, SMART extended log, telemetry decode, and `ocp-nvme.h`.

## Notable Risks And Edge Cases

- Adding a new OCP log output requires updating this callback table, all relevant backends, and `ocp-print.c` dispatch wrappers.
- When JSONC is not built in, JSON dispatch can return `NULL` and produce only the generic `unhandled output format` message.
- Callback signatures expose raw pointers to device-derived packed structures; backends rely on callers to validate allocation sizes and GUIDs.
