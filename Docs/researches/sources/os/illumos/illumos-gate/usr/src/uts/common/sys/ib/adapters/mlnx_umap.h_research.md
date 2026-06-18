# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/mlnx_umap.h

## Role

`mlnx_umap.h` defines the versioned kernel-to-user data ABI for direct userland access to Mellanox HCA resources. It is shared by kernel service drivers such as Tavor, Arbel, and Hermon and user libraries above them.

## Major Definitions

`MLNX_UMAP_IF_VERSION` is set to `2`; comments require consumers of `ibt_ci_data_out()` data to validate revision fields when reading these structures.

The resource type constants identify database entries for UAR pages, BlueFlame pages, process IDs, CQ memory, QP memory, MR user-memory cookies, SRQ memory, and doorbell-record memory. The file also defines a type mask and shift for resource type encoding.

The exported data structures are:
- `mlnx_umap_cq_data_out_t`, describing CQ number, CQ mapping offset/length, CQE count/size, and arm/poll doorbell record mappings and offsets.
- `mlnx_umap_qp_data_out_t`, describing QP number, queue memory mapping, RQ/SQ offsets, descriptor addresses, WQE counts/sizes, send/receive doorbell record mappings, and Hermon SQ headroom.
- `mlnx_umap_srq_data_out_t`, describing SRQ number, queue mapping, descriptor address, WQE count/size, receive doorbell record mapping, and offsets.
- `mlnx_umap_pd_data_out_t`, carrying PD revision and PD number.

## Interfaces

The header declares no functions. It defines data exchanged through other driver/library interfaces.

## Integration Notes

This is an ABI-sensitive header. Any structure change must be coordinated with user libraries such as `udapl_tavor.so.1` and corresponding version checks.
