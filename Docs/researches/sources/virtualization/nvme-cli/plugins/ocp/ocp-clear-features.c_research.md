# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-clear-features.c

## Role

Implements OCP feature clearing and OCP PCIe correctable error counter retrieval helpers used by the main OCP plugin command wrappers.

## Core Helper

`ocp_clear_feature()` centralizes OCP feature clear behavior:

1. Parses device and `--no-uuid`.
2. Opens NVMe device.
3. Unless `--no-uuid` is set, finds the OCP UUID index using `ocp_get_uuid_index()`.
4. Sets bit 31 in the feature value (`clear = 1 << 31`).
5. Sends `nvme_set_features()` with the target feature ID and UUID index.
6. Prints success/failure/status.

The `--no-uuid` option exists because OCP 1.0 does not require UUID index support, while OCP 2.0 does.

## Public Functions

- `ocp_clear_fw_update_history()`: clears OCP firmware update history using `OCP_FID_CFUH`.
- `ocp_clear_pcie_correctable_errors()`: clears OCP PCIe correctable error counters using `OCP_FID_CPCIE`.
- `get_ocp_error_counters()`: issues Get Feature for `OCP_FID_CPCIE`.

## Get Error Counters

`get_ocp_error_counters()` options:

- `--sel` / `-s`: current/default/saved/supported selector.
- `--namespace-id` / `-n`: namespace ID.
- `--no-uuid` / `-u`: skip UUID index detection.

It calls `nvme_get_features()` with the optional UUID index and prints:

- `get-feature:0xC3 <selector> value: <hex>`

If selector is `NVME_GET_FEATURES_SEL_SUPPORTED`, it calls `nvme_show_select_result()`.

## Dependencies

Includes:

- `nvme-cmds.h`
- `nvme-print.h`
- `util/types.h`
- `ocp-nvme.h`
- `ocp-utils.h`

Uses nvme-cli parsing/opening helpers, libnvme feature APIs, and OCP constants from `ocp-nvme.h`.

## Notes

- The file exposes implementation functions declared in `ocp-clear-features.h`.
- Command names are wrapped and registered from `ocp-nvme.c`, not directly in this file.
- Failure to find a UUID index returns immediately for UUID-aware mode.
