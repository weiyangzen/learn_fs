# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/data-area.c

Core Solidigm telemetry data-area parser.

Major responsibilities:
- Parse arbitrary telemetry structures from JSON definitions.
- Calculate telemetry data area offsets from `dalb1..dalb4`.
- Parse table-of-contents entries and telemetry object headers.
- Dispatch NLOG and side-trace parsing.
- Detect OCP telemetry and SKHT format variants.
- Build root JSON arrays `tableOfContents` and `telemetryObjects`.

Dynamic structure parser:
- `sldm_telemetry_structure_parse()` reads fields based on JSON properties: `name`, `type`, `offsetBit`, `sizeBit`, `arraySize`, optional `enum`, optional `memberList`, optional `arraySizeIndicator`.
- Supports scalar values, nested structures, arrays, and multidimensional arrays.
- `telemetry_log_get_value()` extracts bitfields up to 64 bits and sign-extends signed fields.

Data area parsing:
- `telemetry_log_data_area_get_offset()` calculates byte offset and size for DA1-DA4 using telemetry block size.
- `telemetry_log_data_area_toc_parse()` parses TOC records, object metadata, object headers, and configured payload structure.
- If object maps to NLOG, it parses header then calls `solidigm_nlog_parse()`.
- If object name indicates side trace, it calls `sldm_parse_side_trace()`.

Top-level flow:
- `solidigm_telemetry_log_data_areas_parse()` checks OCP/SKHT status, copies config metadata, parses telemetry header, parses COD, then parses configured data areas.

Risks/notes:
- Generic bit extraction does unaligned `uint64_t` loads from log memory.
- Only values fitting within one 64-bit byte-aligned window are supported.
- TOC and object parsing include bounds checks, but payload-specific parsers still depend on accurate config sizes.
