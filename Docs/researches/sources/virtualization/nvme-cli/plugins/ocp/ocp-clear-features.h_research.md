# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-clear-features.h

## Role

Header declaring OCP clear-feature and error-counter functions for use by the main OCP plugin implementation.

## Declarations

- `ocp_clear_fw_update_history()`
- `ocp_clear_pcie_correctable_errors()`
- `get_ocp_error_counters()`

Each uses the nvme-cli command handler signature with `argc`, `argv`, `struct command *`, and `struct plugin *`.

## Dependency Relationship

Implemented by `ocp-clear-features.c`. Called by wrappers in `ocp-nvme.c`.

## Notes

The header has no include guard or `#pragma once`, but it only contains function declarations and copyright/license text.
