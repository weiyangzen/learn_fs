# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/debug-info.c

Parses SKHT debug-info segments from telemetry logs.

Main behavior:
- Requires configuration definitions for:
  - `DebugInfoBlkHeader_t`
  - `DebugInfoHeader_t`
  - `DebugInfoSegHeader_t`
- Parses a block header, then iterates per-core debug info headers until signature mismatch or max core count.
- Valid signature is `0x54321234`.
- Emits arrays `Cores` and `Segments`.

Segment handling:
- Segment ID 3: parses UART log via `sldm_parse_cd_uart_log()`.
- Segment IDs 6, 7, 8: parse tracker info/buffer/context via `sldm_tracker_parse()`.
- Segment count is capped to 16 per core.
- Core count is capped to 255.

Risks/notes:
- Uses fall-through switch intentionally for tracker segment naming, but there are no explicit fall-through annotations.
- Segment payload offset advancement depends on configured structure sizes and segment `nSize`.
