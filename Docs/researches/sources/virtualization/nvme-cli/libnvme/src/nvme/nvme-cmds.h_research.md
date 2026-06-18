# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds.h

## Role

Umbrella public command header. It includes all specification-aligned command initializer headers and declares higher-level command helper functions implemented in `nvme-cmds.c`.

## Includes

- `nvme/ioctl.h`
- `nvme/nvme-types.h`
- `nvme/nvme-cmds-base.h`
- `nvme/nvme-cmds-fabrics.h`
- `nvme/nvme-cmds-mi.h`
- `nvme/nvme-cmds-nvm.h`
- `nvme/nvme-cmds-zns.h`

## Macros

Defines:

- `NVME_FIELD_ENCODE(value, shift, mask)`
- `NVME_FIELD_DECODE(value, shift, mask)`

`nvme-cmds-base.h` also conditionally defines `NVME_FIELD_ENCODE`, so this header preserves backward compatibility for users including only the umbrella header.

## Declared APIs

- `libnvme_get_log()`: chunked log-page retrieval.
- `libnvme_set_etdas()` / `libnvme_clear_etdas()`: manipulate Extended Telemetry Data Area 4 Supported host behavior bit.
- `libnvme_get_uuid_list()`: fetch UUID list if supported.
- Telemetry helpers:
  - `libnvme_get_telemetry_max()`
  - `libnvme_get_telemetry_log()`
  - `libnvme_get_ctrl_telemetry()`
  - `libnvme_get_host_telemetry()`
  - `libnvme_get_new_host_telemetry()`
- ANA helpers:
  - `libnvme_get_ana_log_len_from_id_ctrl()`
  - `libnvme_get_ana_log_atomic()`
  - `libnvme_get_ana_log_len()`
- Namespace/log helpers:
  - `libnvme_get_logical_block_size()`
  - `libnvme_get_lba_status_log()`
- Length helpers:
  - `libnvme_get_feature_length()`
  - `libnvme_get_directive_receive_length()`

## Notes

This header is the public bridge between inline command construction and higher-level helpers that execute commands or compute dynamic sizes.
