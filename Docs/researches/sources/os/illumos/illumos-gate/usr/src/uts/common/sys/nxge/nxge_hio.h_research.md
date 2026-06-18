# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_hio.h

## Purpose
Defines Hybrid I/O support for NXGE in sun4v logical-domain environments: service/guest detection, hypervisor function tables, virtual regions, DMA channel mappings, virtual interrupt state, MAC share callbacks, and HIO lifecycle prototypes.

## Main Interfaces
- Environment macros:
  - `isLDOMservice()`
  - `isLDOMguest()`
  - `isLDOMs()`
- Hypervisor function pointer types for VR assignment/unassignment/info and RX/TX DMA channel assignment/logical-page configuration.
- `nxhv_vr_fp_t`, `nxhv_dc_fp_t`, `nxhv_fp_t`: resolved HV API tables.
- HIO identity and layout:
  - `nxge_hio_type_t`
  - `vr_base_address_t`
  - `vr_region_t`
  - `vp_channel_t`
  - `vpc_type_t`
  - `VP_VC_OFFSET()`
- Virtualized DMA CSR offset enums for RDC and TDC pages.
- Virtual interrupt definitions:
  - `pio_ld_op_t`
  - `hio_ldg_t`
- Core state structures:
  - `nx_rdc_tbl_t`
  - `nxge_hio_vr_t`
  - `nxge_hio_dc_t`
  - `nxge_hio_data_t`
- Prototypes for HIO init/uninit, DMA channel group management, MAC share allocation/bind/query/free, guest register mapping, VR add/release, logical-page config, interrupt add/remove, LDSV access, HV init, and hostinfo setup.

## Dependencies And Relationships
Includes `nxge_mac.h`, `nxge_ipp.h`, `nxge_fflp.h`, and `sys/mac_provider.h`. It bridges NXGE driver state with Crossbow MAC groups/rings and sun4v NIU hypervisor APIs.

## Research Notes
The file explicitly distinguishes service-domain physical channel numbers from guest-domain virtual page/channel numbers. That distinction is central to correctly interpreting `nxge_hio_dc_t.page` versus `nxge_hio_dc_t.channel`.
