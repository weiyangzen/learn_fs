# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-nvm.h

## Role

Defines public NVM Command Set structures, flags, and command data payloads. This is the core header for namespace identification, reservation status, Flexible Data Placement, Dataset Management, Copy command descriptors, and I/O management command fields.

## Key Content

- Defines extended LBA/protection metadata fields:
  - `enum nvme_nvm_id_ns_elbaf`
  - `enum nvme_nvm_id_ns_pif`
  - `enum nvme_nvm_id_ns_lbstm`
  - `enum nvme_nvm_id_ns_pic`
  - `enum nvme_nvm_id_ns_pifa`
  - `struct nvme_nvm_id_ns`
- Defines Identify I/O Command Set capabilities:
  - `enum nvme_id_iocs_iocsc`
- Defines reservation notification log structures and event types:
  - `struct nvme_resv_notification_log`
  - `enum nvme_resv_notify_rnlpt`
- Defines Flexible Data Placement support:
  - `enum nvme_fdp_ruh_type`
  - `struct nvme_fdp_ruh_desc`
  - `enum nvme_fdp_config_fdpa`
  - `struct nvme_fdp_config_desc`
  - `struct nvme_fdp_config_log`
  - `enum nvme_fdp_ruha`
  - `struct nvme_fdp_ruhu_desc`
  - `struct nvme_fdp_ruhu_log`
  - `struct nvme_fdp_stats_log`
  - FDP event enums and event payload structs
  - `struct nvme_fdp_ruh_status_desc`
  - `struct nvme_fdp_ruh_status`
- Defines DSM and Copy command payloads:
  - `struct nvme_dsm_range`
  - `struct nvme_copy_range_f0`
  - `struct nvme_copy_range_f1`
  - `struct nvme_copy_range_f2`
  - `struct nvme_copy_range_f3`
  - `enum nvme_copy_range_sopt`
- Defines reservation status and reservation command constants:
  - `struct nvme_registered_ctrl`
  - `struct nvme_registered_ctrl_ext`
  - `struct nvme_resv_status`
  - `enum nvme_feat_resv_notify_flags`
  - `enum nvme_resv_rtype`
  - `enum nvme_resv_racqa`
  - `enum nvme_resv_rrega`
  - `enum nvme_resv_cptpl`
  - `enum nvme_resv_rrela`
- Defines I/O flags and I/O management operation selectors:
  - `enum nvme_io_control_flags`
  - `enum nvme_io_dsm_flags`
  - `enum nvme_dsm_attributes`
  - `enum nvme_io_mgmt_recv_mo`
  - `enum nvme_io_mgmt_send_mo`

## Dependencies

- Includes `nvme/types.h` and `nvme/nvme-types-base.h`.
- Uses base types such as `struct nvme_timestamp`.
- Uses both little-endian and big-endian fields where the NVMe command set requires them.

## Research Notes

The file is layout-heavy and behavior-free. Many structures represent controller-returned variable-length logs, such as FDP configuration logs and RUH status, and must be walked using descriptor counts and sizes rather than fixed assumptions. Copy descriptors are split by format because protection information and cross-namespace source details differ by command format.

## Filesystem/Storage Relevance

This file describes the command set that block devices expose to higher layers. DSM/deallocate, copy, reservations, write-zeroes related flags, protection information, and FDP all affect how filesystems and storage stacks can optimize placement, discard, copy-offload, and shared-device coordination.
