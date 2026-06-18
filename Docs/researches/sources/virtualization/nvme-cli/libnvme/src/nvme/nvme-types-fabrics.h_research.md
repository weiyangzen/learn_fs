# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-fabrics.h

## Role

Defines libnvme's public NVMe over Fabrics wire-format types. It is a specification mirror for discovery logs, transport addressing, Discovery Information Management, connect command data, host discovery logs, and AVE discovery records.

## Key Content

- Declares fabrics constants such as `NVME_DISC_SUBSYS_NAME`, default RDMA/discovery ports, `NVMF_NQN_SIZE`, and `NVMF_TRSVCID_SIZE`.
- Defines discovery identity and entry flags:
  - `enum nvme_subsys_type`
  - `enum nvmf_disc_eflags`
  - `struct nvmf_disc_log_entry`
  - `struct nvmf_discovery_log`
- Defines transport-specific address subtype data through `union nvmf_tsas`, with RDMA and TCP views.
- Defines transport/address/security enums:
  - `enum nvmf_trtype`
  - `enum nvmf_addr_family`
  - `enum nvmf_treq`
  - `enum nvmf_rdma_qptype`
  - `enum nvmf_rdma_prtype`
  - `enum nvmf_rdma_cms`
  - `enum nvmf_tcp_sectype`
- Provides bit extraction macros using `NVMF_GET`, including `NVMF_TREQ_SECTYPE()` and `NVMF_TREQ_DISABLE_SQFLOW_BIT()`.
- Models Discovery Information Management:
  - `enum nvmf_dim_tas`
  - `enum nvmf_dim_entfmt`
  - `enum nvmf_dim_etype`
  - `enum nvmf_exattype`
  - `struct nvmf_ext_attr`
  - `struct nvmf_ext_die`
  - `union nvmf_die`
  - `struct nvmf_dim_data`
- Models connect and extended discovery payloads:
  - `struct nvmf_connect_data`
  - `struct nvme_host_ext_discover_log`
  - `struct nvme_host_discover_log`
  - `struct nvme_ave_tr_record`
  - `struct nvme_ave_discover_log_entry`
  - `struct nvme_ave_discover_log`

## Dependencies

- Includes `nvme/types.h` and `nvme/nvme-types-base.h`.
- Uses Linux-style endian and fixed-width aliases such as `__u8`, `__le16`, and `__le64`.
- Relies on shared size constants such as `NVME_NQN_LENGTH`, `NVMF_TSAS_SIZE`, and `NVMF_TRADDR_SIZE`.

## Research Notes

This file is data-only and has no executable logic beyond field extraction macros. The main correctness concern is ABI/layout fidelity: users parse controller-returned discovery data directly into these structs. Variable-length structures such as `struct nvmf_ext_attr`, `struct nvmf_ext_die`, `union nvmf_die`, host discovery logs, and AVE discovery logs require callers to validate total lengths before walking flexible arrays.

## Filesystem/Storage Relevance

This is central to NVMe-oF discovery, which is how remote NVMe block devices are enumerated before being attached to the Linux block layer. It does not implement filesystem logic, but it defines the discovery metadata needed for virtualized and fabric-attached block storage.
