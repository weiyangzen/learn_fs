# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-hardware-component-log.c

## Role

Implements retrieval and display dispatch for the OCP Hardware Component Log page.

## Public Entry Point

`ocp_hwcomp_log()` is the command handler. It supports:

- `--comp-id` / `-i`: component identifier, with symbolic values.
- `--list` / `-l`: list component descriptions.

Symbolic component IDs include `asic`, `nand`, `dram`, `pmic`, `pcb`, `cap`, `reg`, `case`, `sn`, `country`, `hw-rev`, `born-on-date`, and `vendor`.

## Component ID Mapping

`hwcomp_id_to_string()` maps enum values to readable descriptions:

- ASIC, NAND, DRAM, PMIC, PCB, capacitor, regulator, case.
- Device serial number, country of origin, global hardware revision, born-on date.
- Vendor unique range `0x8000 ... 0xffff`.
- Reserved fallback.

## Log Retrieval Flow

`ocp_hwcomp_log()`:

1. Parses command options and opens device.
2. Calls `get_hwcomp_log()`.

`get_hwcomp_log()`:

1. Validates output format.
2. Calls `get_hwcomp_log_data()`.
3. Calls `ocp_show_hwcomp_log(&log, id, list, fmt)`.
4. Frees allocated descriptor data.

`get_hwcomp_log_data()`:

1. Retrieves OCP UUID index via `ocp_get_uuid_index()`.
2. Fetches the fixed header portion up to `offsetof(struct hwcomp_log, desc)`.
3. Converts the 128-bit log size.
4. For log version 1, treats size as DWORD count and multiplies by 4 bytes.
5. Validates size is larger than the header.
6. Allocates descriptor payload.
7. Fetches remaining payload using Get Log Page with log page offset.
8. Stores payload pointer in `log->desc`.

## Logging Helpers

The file defines `print_info_array()` and `print_info_error()` macros that emit diagnostic information only when `log_level >= LIBNVME_LOG_INFO`.

There is a disabled `HWCOMP_DUMMY` block containing a large dummy log byte array for local testing if enabled at compile time.

## Dependencies

Includes:

- `common.h`
- `util/types.h`
- `logging.h`
- `nvme-print.h`
- `ocp-hardware-component-log.h`
- `ocp-print.h`
- `ocp-utils.h`

Uses libnvme Get Log Page helpers, nvme-cli output-format validation, OCP UUID lookup, and OCP print dispatch.

## Notes

- The log header has an inline pointer field `desc`; only bytes before that pointer are fetched for the header.
- `desc` is heap allocated and must be freed by the caller.
- If the second log fetch fails, `log->desc` is freed but not reset before returning; caller exits on error, so it is not reused.
- The command is display-oriented and delegates detailed parsing/printing to `ocp_show_hwcomp_log()`.
