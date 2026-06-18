# File Research: sources/virtualization/nvme-cli/plugins/nvidia/nvidia-nvme.c

## Role

Implements NVIDIA vendor-specific Identify Controller display extension for nvme-cli.

The plugin adds an `id-ctrl` command that delegates most Identify Controller behavior to the shared nvme-cli `__id_ctrl()` helper, while providing a vendor-specific callback for the Identify Controller vendor-specific bytes.

## Main Data Structure

`struct nvme_vu_id_ctrl_field` overlays the vendor-specific Identify Controller area:

- `json_rpc_2_0_mjr`
- `json_rpc_2_0_mnr`
- `json_rpc_2_0_ter`
- `reserved0[1018]`

These fields are little-endian 16-bit values.

## Output Logic

`nvidia_id_ctrl()` casts the vendor-specific pointer to `struct nvme_vu_id_ctrl_field`, formats the JSON-RPC 2.0 version as a concatenated hex string:

`0x%04x%04x%04x`

It prints either:

- normal output: `json_rpc_2_0_ver : <value>`
- JSON output: adds key `json_rpc_2_0_ver`

`json_nvidia_id_ctrl()` adds that key to the JSON object.

## Public Command Handler

`id_ctrl()` calls:

`__id_ctrl(argc, argv, acmd, plugin, nvidia_id_ctrl)`

This means standard nvme-cli Identify Controller parsing, device opening, and output handling remain centralized outside this file.

## Dependencies

Includes:

- libnvme
- `common.h`
- `nvme.h`
- `plugin.h`
- `nvidia-nvme.h`

## Notes

- The file is intentionally small and callback-based.
- It does not do independent device/model validation.
- All command registration is in `nvidia-nvme.h`.
