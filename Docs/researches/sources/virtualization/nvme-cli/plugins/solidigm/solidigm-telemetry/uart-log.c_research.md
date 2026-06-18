# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/uart-log.c

Parses UART log segments from SKHT/debug telemetry.

Main behavior:
- Validates offset and size against telemetry log size.
- Treats each UART entry as 192 bytes.
- Uses config structures:
  - `UartLogBufHeader`
  - `UartLogBufBody`
- Parses each entry header and body via `sldm_telemetry_structure_parse()`.
- Adds entries under output key `"uart_log"`.

Risks/notes:
- Partial trailing entries are ignored.
- Missing config definitions cause individual entry parsing to fail but the command still returns through the outer parser path.
