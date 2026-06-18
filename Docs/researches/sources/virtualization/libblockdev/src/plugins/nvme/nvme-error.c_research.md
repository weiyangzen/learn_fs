# File Research: sources/virtualization/libblockdev/src/plugins/nvme/nvme-error.c

## Role
Implements the NVMe plugin error domain and internal conversion helpers from libnvme status/errno values to libblockdev `GError`s.

## Error Domain
- `bd_nvme_error_quark()` returns the plugin's static GLib error quark.

## Status Conversion
- `_nvme_status_to_error(status, fabrics, error)`:
  - clears the error for status 0;
  - maps negative status through `errno`, treating `EWOULDBLOCK` as `BD_NVME_ERROR_BUSY` and other errno values as generic failure;
  - maps positive NVMe status by status-code type into generic, command-specific, media, path, or vendor-specific libblockdev error codes;
  - uses `nvme_status_to_string(status, fabrics)` for the message.

## Fabrics Error Conversion
- `_nvme_fabrics_errno_to_gerror(result, _errno, error)`:
  - clears the error for result 0;
  - maps libnvme fabrics connection errors beginning at `ENVME_CONNECT_RESOLVE` into invalid-argument, connect, already-connected, invalid, address-in-use, no-device, operation-not-supported, or refused codes;
  - otherwise falls back to process `errno`, again treating `EWOULDBLOCK` as busy and other cases as generic failure.

## Notes
The file intentionally keeps NVMe error policy centralized so other NVMe plugin files can report consistent GLib errors for both admin/status-code paths and NVMe-oF connection paths.
