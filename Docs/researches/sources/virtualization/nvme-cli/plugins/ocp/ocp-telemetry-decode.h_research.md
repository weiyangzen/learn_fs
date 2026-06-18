# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-telemetry-decode.h

## Role

`ocp-telemetry-decode.h` is the schema and interface header for the OCP telemetry decoder. It defines telemetry statistic IDs, event class IDs, event-specific ID-to-string lookup tables, binary layout structs for telemetry/string logs, string constants used in output, parser option structures, and public function prototypes implemented by `ocp-telemetry-decode.c`.

## Global Buffers

The header declares:

- `extern __u8 *ptelemetry_buffer`
- `extern __u8 *pstring_buffer`

The decoder implementation treats these as the active telemetry log buffer and C9 string-log buffer. Most parser functions take offsets/options but still rely on these globals for the underlying binary content.

## ID Enumerations and String Tables

The first half of the file is a large set of OCP/NVMe telemetry identifiers and their display strings:

- `enum TELEMETRY_STATISTIC_ID` and `telemetry_stat_id_str[]`.
- `enum TELEMETRY_EVENT_CLASS_TYPE` and `telemetry_event_class_str[]`.
- Timestamp, PCIe, NVMe, reset, boot sequence, firmware assert, temperature, media debug, media wear, and virtual FIFO event ID enums.
- PCIe state, speed, and width enums.

The static inline helpers at the end of this table section use `ARGSTR()` and `arg_str()` to safely return `"unrecognized"` if an index is out of range or has no string. The implementation file uses these helpers in direct printer paths.

## Constants and Output Labels

The header defines key telemetry sizing constants:

- `TELEMETRY_HEADER_SIZE`, `TELEMETRY_BYTE_PER_BLOCK`, and `OCP_TELEMETRY_DATA_BLOCK_SIZE` are 512-byte based.
- `SIZE_OF_DWORD` is 4 and is used throughout string-log, stats, and FIFO calculations.
- `MAX_NUM_FIFOS` is 16.
- `DEFAULT_TELEMETRY_LOG`, `DEFAULT_STRING_BIN`, and `DEFAULT_OUTPUT_FORMAT_JSON` provide CLI defaults.

It also defines output string constants such as `STR_LOG_PAGE_HEADER`, `STR_REASON_IDENTIFIER`, `STR_DA_1_STATS`, `STR_EVENT_IDENTIFIER`, `STR_VU_DATA`, and separator lines used consistently by text and JSON paths.

## Binary Layout Structures

The header carries two groups of layout definitions. Older/general structures include `telemetry_initiated_log`, `telemetry_stats_desc`, `telemetry_event_desc`, `event_fifo`, and `telemetry_data_area_1`. The newer OCP-specific packed definitions include:

- `nvme_ocp_telemetry_reason_id`
- `nvme_ocp_telemetry_common_header`
- `nvme_ocp_telemetry_host_initiated_header`
- `nvme_ocp_telemetry_controller_initiated_header`
- `nvme_ocp_telemetry_smart`
- `nvme_ocp_telemetry_smart_extended`
- `nvme_ocp_header_in_da1`
- `nvme_ocp_telemetry_statistic_descriptor`
- `nvme_ocp_telemetry_event_descriptor`
- class-specific payload structs for timestamp, PCIe, NVMe, media wear, and common VU data
- string-log table entries and `nvme_ocp_telemetry_string_header`

These structures encode OCP telemetry offsets directly in C type layout and comments include byte positions for maintainability.

## String Log Structures

The header defines both `telemetry_str_log_format` and the OCP-specific `nvme_ocp_telemetry_string_header`, plus table entry structs for statistics, event, and VU event string lookup. The string log format is organized around DWORD offsets/sizes for statistics identifier string table, event string table, VU event string table, ASCII table, and 16 FIFO ASCII labels.

## Parser Options and Prototypes

`struct ocp_telemetry_parse_options` carries input/output choices:

- telemetry log filename
- string log filename
- output file prefix
- output format
- requested data area
- telemetry type

The prototypes expose the full parser surface: top-level telemetry parsing, string lookup, DA offset calculation, statistics parsing, FIFO parsing, event-class parsing, and normal/JSON printing.

## Dependencies and Integration

The header includes nvme-cli headers `nvme.h`, `nvme-print.h`, `util/utils.h`, `common.h`, and `ocp-nvme.h`. It assumes `struct json_object` is visible from included nvme-cli JSON support and that packed layout support is available through the project headers.

## Notable Risks

This header embeds many static const string arrays in a header, meaning each translation unit that includes it gets its own copy. That is acceptable for plugin-local code but increases object size. Some enum comments and names contain typos or legacy names, but the numeric values are the important ABI. Several packed structures contain bitfields; those are convenient for local parsing but can be compiler-layout sensitive compared with explicit mask/shifts.
