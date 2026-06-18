# File Research: sources/virtualization/nvme-cli/plugins/ocp/meson.build

## Role

Meson build snippet that adds OCP plugin source files to the `plugin_sources` list.

## Always-Built Sources

The file appends these OCP sources:

- `ocp-utils.c`
- `ocp-nvme.c`
- `ocp-clear-features.c`
- `ocp-smart-extended-log.c`
- `ocp-fw-activation-history.c`
- `ocp-telemetry-decode.c`
- `ocp-hardware-component-log.c`
- `ocp-print.c`
- `ocp-print-stdout.c`
- `ocp-print-binary.c`

## Conditional Source

If `json_c_dep.found()` is true, it also adds:

- `ocp-print-json.c`

## Dependency Relationship

The files researched in this group are included here:

- `ocp-clear-features.c`
- `ocp-fw-activation-history.c`
- `ocp-hardware-component-log.c`

Their JSON output support depends indirectly on the conditional inclusion of `ocp-print-json.c`.

## Notes

This file contains no runtime code. It controls compilation membership for the OCP plugin implementation.
