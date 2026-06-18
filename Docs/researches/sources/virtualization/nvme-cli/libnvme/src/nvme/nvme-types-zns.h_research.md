# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-zns.h

## Role

Defines public Zoned Namespace Command Set structures and enums. These types describe ZNS identify data, changed zone logs, zone descriptors, zone reports, and zone management command selectors.

## Key Content

- Defines LBA format extension data:
  - `struct nvme_zns_lbafe`
- Defines ZNS identify namespace/controller structures:
  - `struct nvme_zns_id_ns`
  - `struct nvme_zns_id_ctrl`
- Defines changed zone log format:
  - `struct nvme_zns_changed_zone_log`
- Defines zone descriptor type, attributes, and state:
  - `enum nvme_zns_zt`
  - `enum nvme_zns_za`
  - `enum nvme_zns_zs`
  - `struct nvme_zns_desc`
- Defines report zones payload:
  - `struct nvme_zone_report`
- Defines zone management send/receive selectors:
  - `enum nvme_zns_send_action`
  - `enum nvme_zns_recv_action`
  - `enum nvme_zns_report_options`

## Dependencies

- Includes `nvme/types.h` and `nvme/nvme-types-base.h`.
- Uses constants such as `NVME_ZNS_CHANGED_ZONES_MAX`.
- Uses endian-tagged fields for controller wire data.

## Research Notes

The structures directly mirror ZNS specification data. `struct nvme_zone_report` has a flexible `entries[]` array, so callers must size buffers according to requested report length and returned zone count. Zone states and report filters are explicit enum values, making the header the canonical mapping from numeric command fields to libnvme names.

## Filesystem/Storage Relevance

ZNS affects filesystem and block allocation strategy because writes must respect zone state and write-pointer constraints. This file supplies the user-space type definitions needed by tools that inspect and manage zoned NVMe namespaces.
