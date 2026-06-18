# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/cod.c

Parses Solidigm COD/OEM data map content referenced by the telemetry reason identifier.

Main behavior:
- Looks in root JSON at `telemetryHeader.reasonIdentifier.oemDataMapOffset`.
- Validates the COD header is within `tl->log_size`.
- Checks big-endian signature `0x504D4443`.
- Validates `MapSizeInBytes`.
- Iterates `EntryCount` items and adds decoded values under root key `"cod"`.

Data model:
- Packed `cod_header`, `cod_item`, and flexible `cod_map`.
- Field IDs are mapped to labels like media read count, serial number, firmware revision, latency metrics, power loss status, wear, and defect counters.

Supported field types:
- Integer, signed or unsigned.
- Float.
- String.
- Two-byte ASCII.
- Four-byte ASCII.

Risks/notes:
- Offset validation contains `if (item.DataFieldOffset + item.DataFieldOffset > tl->log_size)`, likely intended to check offset plus field size.
- Integer decoding always reads 64 bits regardless of `DataFieldSizeInBytes`.
