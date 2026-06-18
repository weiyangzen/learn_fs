# File Research: sources/virtualization/nvme-cli/plugins/nbft/nbft-plugin.h

## Role

Command registration header for the NBFT nvme-cli plugin.

## Registered Plugin

Plugin name: `nbft`.

Description: `ACPI NBFT table extensions`.

Version source: `NVME_VERSION`.

## Registered Command

- `show`: `Show contents of ACPI NBFT tables`, mapped to `show_nbft`.

## Dependency Relationship

Included by `nbft-plugin.c` with `CREATE_CMD` defined. Uses nvme-cli command macros from `cmd.h` and finalizes generation through `define_cmd.h`.

## Notes

The header contains no data parsing logic. It only declares the plugin command surface.
