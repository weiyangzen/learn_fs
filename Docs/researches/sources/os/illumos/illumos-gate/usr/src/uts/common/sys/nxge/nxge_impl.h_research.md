# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_impl.h

## Purpose
Defines the internal NXGE driver implementation interface: OS includes, hypervisor API versions, DMA/common macros, driver status and platform enums, DMA allocation state, logical interrupt software state, PCI/register mappings, alternate MAC bookkeeping, cross-module includes, and implementation prototypes.

## Main Interfaces
- NIU HV API version constants and sun4v HV API numbers.
- DMA and NPI access macros:
  - `DMA_COMMON_*`
  - `NPI_*_HANDLE_SET/GET`
  - descriptor and DMA cookie helpers.
- Core types/enums:
  - `nxge_status_t`
  - `dev_func_shared_t`
  - `dma_method_t`
  - `nxge_rx_block_size_t`
  - `dma_size_t`
  - `dma_type_t`
  - `rx_page_state_t`
  - `niu_type_t`
  - `niu_hw_type_t`
  - `platform_type_t`
  - `cfg_type_t`
  - output/debug message enums.
- DMA state:
  - `nxge_dma_common_t`
  - `nxge_dma_pool_t`
- Logical interrupt state:
  - `nxge_ldg_t`
  - `nxge_ldv_t`
  - interrupt handler typedefs.
- PCI/register mapping:
  - `pci_cfg_t`
  - `dev_regs_t`
- MAC address management:
  - `nxge_mac_addr_t`
  - `nxge_mmac_t`
  - `nxge_mmac_stats_t`
- Main prototype groups for classify/FFLP, kstats, hardware reset/ioctl/interrupts, TX send, RXDMA config, ndd parameters, virtual/FZC, MAC/PHY/MII/MDIO, ESPC/SPROM, debug, buffer free, and sun4v weak HV symbols.

## Dependencies And Relationships
Includes Solaris networking, streams, DDI/FMA, MAC provider, hypervisor, and many NXGE internal headers. It is the central internal include used by NXGE implementation `.c` files rather than a narrow hardware layout header.

## Research Notes
The file encodes many board/product identities, including Neptune, Huron, Maramba, Alonso, Rock, N2/NIU, RF/NIU, and specific board model strings. It also contains weak sun4v hypervisor declarations so the same driver can bind where HV services may or may not be present.
