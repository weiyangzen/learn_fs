# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/skht.c

Handles SKHT telemetry layout detection and segment parsing.

Main behavior:
- `sldm_telemetry_check_for_skhT()` detects signature `0x54686B73`.
- Non-OCP logs check the start of data area 2.
- OCP logs check after DA3 segment headers.
- `sldm_telemetry_skhT_parse()` parses `HynixHeader` and `BuildInfo` from config.
- `sldm_telemetry_sktT_segment_parse()` parses `SegmentHeader`, then iterates segment descriptors.

Segment dispatch:
- Descriptions beginning with `TRACKER_DATA` call `sldm_tracker_parse()`.
- `UART_LOG_INFO` stores a string from the log.
- `DEBUG_INFO` calls `sldm_debug_info_parse()`.

Config versions:
- Uses `SKT_VER_MAJOR` `47837` and `SKT_VER_MINOR` `49374`.

Risks/notes:
- Segment payload offsets are calculated relative to `NVME_LOG_TELEM_BLOCK_SIZE + descriptor offset`.
- Converts `nDescription` and `nTypeName` byte arrays into strings in-place for readability.
