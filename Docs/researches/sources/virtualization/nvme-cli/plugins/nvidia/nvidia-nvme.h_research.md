# File Research: sources/virtualization/nvme-cli/plugins/nvidia/nvidia-nvme.h

## Role

Command registration header for the NVIDIA nvme-cli plugin.

## Registered Plugin

Plugin name: `nvidia`.

Description: `NVIDIA vendor specific extensions`.

Version source: `NVME_VERSION`.

## Registered Command

- `id-ctrl`: mapped to `id_ctrl`, described as `Send NVMe Identify Controller`.

## Dependency Relationship

Included by `nvidia-nvme.c` with `CREATE_CMD` defined. Uses nvme-cli plugin macros from `cmd.h` and finalizes via `define_cmd.h`.

## Notes

This header contains only command registration and no parsing or device logic.
