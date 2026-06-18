# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-telemetry-decode.c

## Role

`ocp-telemetry-decode.c` is the implementation side of OCP telemetry log decoding. It consumes global telemetry and string-log buffers declared in the companion header, interprets OCP/NVMe telemetry headers, statistics descriptors, event FIFO descriptors, and optional vendor-unique strings, then emits either plain text or JSON depending on build configuration and caller options.

The file is data-format driven. It contains parser tables for fixed structures, static fallback names for statistic identifiers, helper printers, string-table lookup logic, event-class parsers, statistics parsers, event FIFO iteration, and top-level normal/JSON output functions.

## Main Data Tables

The top of the file defines display-oriented `struct request_data` arrays for generic parsing:

- `host_log_page_header` and `controller_log_page_header` describe the generic 512-byte telemetry log header layouts.
- `reason_identifier` describes the embedded OCP reason identifier.
- `ocp_header_in_da1` describes the OCP data-area-1 header, including profile, string-log size, firmware revision, statistics ranges, and up to 16 FIFO locations.
- `smart` and `smart_extended` describe the standard SMART/health and OCP extended SMART blocks embedded after the DA1 OCP header.

`statistic_identifiers_map` provides fallback text for OCP statistic IDs `0x00` through `0x6f` when a telemetry string log does not provide an ASCII string entry. The same file also has early legacy-style printers (`print_vu_event_data`, `print_stats_desc`, `print_telemetry_fifo_event`) that use the ID-to-string helpers from the header and print decoded event details directly.

## String Log Lookup

The string lookup path is centered on `parse_ocp_telemetry_string_log()`. It dispatches to:

- `get_statistic_id_ascii_string()` for statistic identifier strings.
- `get_event_id_ascii_string()` for event ID strings.
- `get_vu_event_id_ascii_string()` for vendor-unique event ID strings.
- FIFO ASCII names stored directly in `nvme_ocp_telemetry_string_header::fifo_ascii_string`.

All table offsets and sizes are treated as DWORD counts and multiplied by `SIZE_OF_DWORD`. If a statistic string is missing and the ID is in the fixed OCP range, the parser falls back to `statistic_identifiers_map`.

## Offset Calculation

`get_telemetry_das_offset_and_size()` validates input pointers, selects the proper telemetry header size based on `NVME_LOG_LID_TELEMETRY_HOST` versus `NVME_LOG_LID_TELEMETRY_CTRL`, and calculates start offsets and byte sizes for DA1 through DA4. It uses the telemetry common header's last-block fields and the OCP 512-byte block size. These offsets are reused by statistics and FIFO parsing.

## Event Parsing

When `CONFIG_JSONC` is enabled, the file provides detailed event parsers:

- `parse_time_stamp_event()` handles timestamp class events with 8 bytes of class-specific data and optional VU payload.
- `parse_pcie_event()` handles 4 bytes of PCIe class-specific data and optional VU payload.
- `parse_nvme_event()` handles 8 bytes of NVMe class-specific data and optional VU payload.
- `parse_media_wear_event()` handles 12 bytes of media-wear class-specific data and optional VU payload.
- `parse_common_event()` handles classes whose event body is treated as VU event identifier plus VU data.

Each parser supports three output modes through the same code path: JSON object population, file-backed text output, or stdout text output. They add common fields such as class-specific data, VU event ID, VU event string, and VU data. Size checks are minimal and assume the containing FIFO range is trustworthy.

## FIFO Parsing

`parse_event_fifo()` is the core FIFO walker. For a single FIFO it:

1. Resolves the FIFO name from the string log.
2. Creates a JSON array or prints a text section header.
3. Iterates event descriptors until the FIFO size is exhausted or a reserved class terminator is found.
4. Emits generic descriptor fields: debug class, event ID, event string, and data size.
5. Dispatches class-specific parsing for timestamp, PCIe, NVMe, reset, boot, firmware assert, temperature, media, media wear, and statistic snapshot classes.
6. Advances by descriptor size plus event data size.

`parse_event_fifos()` builds a 16-entry `nvme_ocp_event_fifo_data` array from DA1 header metadata, filters FIFOs by the requested data area, calculates FIFO byte offsets from DWORD starts/sizes, and invokes `parse_event_fifo()` for each matching FIFO. It supports DA1 and DA2 only in the actual pointer selection.

## Statistics Parsing

`parse_statistics()` selects the statistics region for DA1 or DA2 using the `da1_statistic_start`, `da1_statistic_size`, `da2_statistic_start`, and `da2_statistic_size` fields in the OCP DA1 header. It walks `nvme_ocp_telemetry_statistic_descriptor` entries until the configured region ends or a reserved statistic ID terminator is seen.

`parse_statistic()` emits descriptor metadata and the statistic payload. Three bad-block statistics get special field names and split percentage/raw values:

- `MAX_DIE_BAD_BLOCK_ID`
- `MAX_NAND_CHANNEL_BAD_BLOCK_ID`
- `MIN_NAND_CHANNEL_BAD_BLOCK_ID`

All other statistic data is emitted as a formatted variable-size hex string.

## Top-Level Output

`print_ocp_telemetry_normal()` emits text to stdout or `<output_file>.txt`. It prints the log header, reason identifier, DA1 OCP header, SMART, extended SMART, DA1 statistics, DA1 FIFOs, and optionally DA2 statistics/FIFOs when `options->data_area == 2`.

`print_ocp_telemetry_json()` builds a JSON object with the same major sections and writes it to `<output_file>.json` or prints it. It always uses `host_log_page_header` for the top header in the JSON path, even though the normal path checks `options->telemetry_type` for host versus controller.

## Dependencies and Integration

This file depends on nvme-cli/libnvme types and helpers from `common.h`, `nvme.h`, `plugin.h`, `util/types.h`, `nvme-print.h`, and `ocp-telemetry-decode.h`. It relies heavily on helpers such as `generic_structure_parser()`, `print_formatted_var_size_str()`, JSON helper functions, `nvme_show_error()`, and endianness conversion macros. Its public entry points are declared in `ocp-telemetry-decode.h`.

## Notable Risks

The parser frequently casts unaligned byte pointers directly to packed or scalar types and does only limited bounds validation inside telemetry regions. Many values are consumed without little-endian conversion before arithmetic or JSON formatting. String lookup copies `ascii_id_length + 1` bytes into caller-provided buffers without checking destination capacity. `parse_event_fifo()` allocates 41 bytes for `description` but clears only `sizeof(40)` bytes, and some error paths return without freeing that allocation. These are acceptable for a diagnostic decoder in trusted tooling contexts but should be reviewed carefully before using this parser on untrusted telemetry blobs.
