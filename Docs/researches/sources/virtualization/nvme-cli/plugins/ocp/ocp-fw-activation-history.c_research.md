# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-fw-activation-history.c

## Role

Implements retrieval and validation of the OCP firmware activation history log.

## Public Entry Point

`ocp_fw_activation_history_log()` is the command handler implementation. It is wrapped by the main OCP plugin and declared in `ocp-fw-activation-history.h`.

## Flow

1. Parses and opens the NVMe device.
2. Initializes a zeroed `struct fw_activation_history`.
3. Best-effort retrieves OCP UUID index with `ocp_get_uuid_index()`.
4. Builds a Get Log Page command for `OCP_LID_FAHL_OBSOLETE`.
5. Encodes UUID index into `cdw14`.
6. Calls `libnvme_get_log()`.
7. Validates returned log page GUID against `ocp_fw_activation_history_guid`.
8. Validates output format through `validate_output_format()`.
9. Prints through `ocp_fw_act_history()`.

## GUID Validation

The expected firmware activation history GUID is stored as a 16-byte array:

`6D 79 9A 76 B4 DA F6 A3 E2 4D B2 8A AC F3 1C D1`

If the log fetch succeeds but GUID differs, the function returns `-EINVAL`.

## Dependencies

Includes:

- `common.h`
- `nvme-print.h`
- `ocp-fw-activation-history.h`
- `ocp-nvme.h`
- `ocp-print.h`
- `ocp-utils.h`

Uses libnvme command initialization and nvme-cli print dispatch.

## Notes

- UUID index detection is best effort; correctness is enforced by GUID comparison.
- The function fetches a fixed-size `struct fw_activation_history`.
- Printing is delegated to the OCP print abstraction, allowing stdout/JSON/binary behavior elsewhere.
