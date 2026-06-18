# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-utils.c

## Role

`ocp-utils.c` provides small shared helpers for OCP plugin commands. It centralizes OCP UUID handling, simple OCP get-log command construction, and detection of a specific TCG activity persistent-event encoding.

## UUID Handling

The file defines the OCP UUID as `ocp_uuid`, a 16-byte constant:

`c1 94 d5 5b e0 94 47 94 a2 1d 29 99 8f 56 be 6f`

`ocp_find_uuid_index()` uses `libnvme_find_uuid()` to locate this UUID in an identify UUID list. It returns zero and stores the positive index when found, initializes `*index` to zero, and returns `-errno` if the UUID cannot be found.

`ocp_get_uuid_index()` retrieves the UUID list via `nvme_identify_uuid_list()` and delegates to `ocp_find_uuid_index()`.

## Simple Log Retrieval

`ocp_get_log_simple()` creates a `libnvme_passthru_cmd` for an OCP DSSD log ID. It:

1. Attempts to retrieve the OCP UUID index.
2. Calls `nvme_init_get_log()` using `NVME_NSID_ALL`, the requested log ID, `NVME_CSI_NVM`, the caller buffer, and the requested length.
3. Encodes the UUID index into `cdw14`.
4. Calls `libnvme_get_log()`.

The helper ignores the return value of `ocp_get_uuid_index()`, so a UUID lookup failure leaves `uidx` at whatever value the callee set, usually zero.

## Persistent Event Predicate

`ocp_is_tcg_activity_event()` inspects a persistent event entry and associated vendor-specific descriptor. It returns true only when the event is vendor-specific and exact header/length/type constants match the TCG activity event shape:

- event type is `NVME_PEL_VENDOR_SPECIFIC_EVENT`
- event header length is `0x15`
- vendor-specific information length is `0x04`
- event length is `0x30`
- vendor-specific event code is `0x01`
- vendor-specific event data length is `0x26`
- vendor-specific data type is binary

## Dependencies and Integration

The file includes `nvme-cmds.h`, `ocp-nvme.h`, `ocp-utils.h`, `types.h`, and utility type headers. It works at the libnvme transport-handle layer and is meant to be shared by OCP command implementations.

## Notable Risks

`ocp_get_log_simple()` does not propagate UUID lookup failure before issuing the log command. That may be intentional for devices where UUID index zero is acceptable, but it means callers cannot distinguish “UUID missing” from “log read attempted at index zero”.
