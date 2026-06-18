# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-smart-extended-log.c

## Role

`ocp-smart-extended-log.c` implements the `smart-add-log` command for the OCP plugin. It retrieves the OCP C0 SMART / Health Information Extended log page, validates its GUID, and dispatches output through the OCP print layer.

## Control Flow

`ocp_smart_add_log()` parses and opens the target NVMe device, then calls `get_c0_log_page()` with the global output format and output format version.

`get_c0_log_page()` validates the output format, allocates a 512-byte C0 buffer, obtains the OCP UUID index, initializes an NVMe get-log command for `OCP_LID_SMART`, encodes the UUID index into `cdw14`, and submits the request with `libnvme_get_log()`. On success it compares the returned `log_page_guid` against the expected SMART cloud attribute GUID before calling `ocp_smart_extended_log()`.

The output format version is passed through to the JSON printer so callers can request the v1 or v2 SMART JSON schema.

## Dependencies

The file depends on libnvme passthrough/get-log APIs, nvme-cli argument parsing and output format validation, `ocp-utils.h` for UUID index lookup, `ocp-nvme.h` for the OCP log identifier, `ocp-smart-extended-log.h` for the C0 structure, and `ocp-print.h` for output dispatch.

## Notable Risks And Edge Cases

- The command calls `ocp_get_uuid_index()` but does not check its return value before encoding `uidx`; failure behavior depends on what value remains in `uidx`.
- It prints NVMe status for non-JSON formats even before GUID validation, so normal output mixes status and decoded content.
- GUID mismatch diagnostics print bytes with `%x` rather than zero-padded hex, which can make comparisons harder to read.
- The allocation size is fixed at 512 bytes and assumes the structure remains exactly one C0 log page.
