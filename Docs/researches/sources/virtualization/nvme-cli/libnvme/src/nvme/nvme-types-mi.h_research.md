# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-mi.h

## Role

Defines public NVMe Management Interface data structures and enums. It is a specification-facing header for MI command effects, port/controller information, subsystem health, controller health, and VPD records.

## Key Content

- Defines MI command supported/effects flags through `enum nvme_mi_cmd_supported_effects` and `NVME_MI_CMD_SUPPORTED_EFFECTS_SCOPE()`.
- Defines the MI command effects log:
  - `struct nvme_mi_cmd_supported_effects_log`
- Models MI read data structures:
  - `struct nvme_mi_read_nvm_ss_info`
  - `struct nvme_mi_port_pcie`
  - `struct nvme_mi_port_smb`
  - `struct nvme_mi_read_port_info`
  - `struct nvme_mi_read_ctrl_info`
  - `struct nvme_mi_osc`
  - `struct nvme_mi_read_sc_list`
- Defines subsystem and SMART warning bit fields:
  - `enum nvme_mi_nss`
  - `enum nvme_mi_sw`
  - extraction macros such as `NVME_MI_NSS_NRDY()` and `NVME_MI_SW_RO()`
- Models health data:
  - `struct nvme_mi_nvm_ss_health_status`
  - `enum nvme_mi_ccs`
  - `struct nvme_mi_ctrl_health_status`
  - `enum nvme_mi_csts`
  - `enum nvme_mi_cwarn`
- Models Vital Product Data:
  - `struct nvme_mi_vpd_mra`
  - `struct nvme_mi_vpd_ppmra`
  - `struct nvme_mi_vpd_telem`
  - `enum nvme_mi_elem`
  - `struct nvme_mi_vpd_tra`
  - `struct nvme_mi_vpd_mr_common`
  - `struct nvme_mi_vpd_hdr`

## Dependencies

- Includes `nvme/types.h` and `nvme/nvme-types-base.h`.
- Uses shared constants such as `NVME_LOG_MI_CMD_SUPPORTED_EFFECTS_MAX` and `NVME_LOG_MI_CMD_SUPPORTED_EFFECTS_RESERVED`.
- Depends on endian-tagged aliases for wire-format fields.

## Research Notes

The file has no behavior; it provides stable type definitions for MI clients and transports. Several structures include flexible or zero-length arrays, including `nvme_mi_read_sc_list`, `nvme_mi_vpd_telem`, `nvme_mi_vpd_tra`, and `nvme_mi_vpd_hdr`. Callers must handle descriptor lengths carefully when parsing device-provided VPD or command-list payloads.

## Filesystem/Storage Relevance

MI supports out-of-band management of NVMe devices, including health and topology discovery. This helps inventory and diagnose storage devices that may later expose namespaces to the OS block layer.
