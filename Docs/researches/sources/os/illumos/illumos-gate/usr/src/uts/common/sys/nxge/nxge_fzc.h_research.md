# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_fzc.h

## Purpose
Declares initialization and configuration routines for function-zero controlled NXGE resources: interrupts, logical pages, TX/RX DMA partitioning, RDC tables, RED, DRR, and system error masks.

## Main Interfaces
- Interrupt setup:
  - `nxge_fzc_intr_init()`
  - `nxge_fzc_intr_ldg_num_set()`
  - `nxge_fzc_intr_tmres_set()`
  - `nxge_fzc_intr_sid_set()`
- RX/TX logical page programming:
  - `nxge_fzc_dmc_rx_log_page_vld()`
  - `nxge_fzc_dmc_rx_log_page_mask()`
  - `nxge_init_fzc_rxdma_channel_pages()`
  - `nxge_init_fzc_txdma_channel_pages()`
- TX/RX DMA initialization:
  - `nxge_init_fzc_tdc()`
  - `nxge_init_fzc_rdc()`
  - `nxge_init_fzc_txdma_channel()`
  - `nxge_init_fzc_rxdma_channel()`
  - port/common initialization variants.
- RDC table binding:
  - `nxge_init_fzc_rdc_tbl()`
  - `nxge_fzc_rdc_tbl_bind()`
  - `nxge_fzc_rdc_tbl_unbind()`
- RED/clearlog/DRR helpers and logical device group setup.
- Optional sun4v NIU logical-page workaround entry points under `NIU_LP_WORKAROUND`.

## Dependencies And Relationships
Includes `npi_vir.h`. The prototypes are repeated or consumed from `nxge_impl.h`, and operate on `p_nxge_t`, DMA ring types, and RDC group types defined in other NXGE headers.

## Research Notes
This is a declaration-only coordination header. It separates FZC-owned hardware programming from per-block RX/TX/MAC logic.
