# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_hw.h

## Purpose
Aggregates per-block NXGE hardware headers and defines global device register layouts for function control, partitioning, DMA binding, logical interrupt devices/groups, reset, system error status/masks, SMX/debug/GPIO/PIM, and logical page translation.

## Main Interfaces
- Includes per-block hardware ABIs:
  - FFLP, IPP, MAC, RXDMA, TXC, TXDMA, ZCP, ESPC, N2 ESR, SRAM, and PHY hardware headers.
- Core types:
  - `dc_map_t`
  - `lg_map_t`
  - `nxge_mode_t`
- Function/partition control:
  - `DEV_FUNC_SR_REG`
  - `dev_func_sr_t`
  - `MULTI_PART_CTL_REG`
  - `multi_part_ctl_t`
  - `VADDR_REG`
  - `DMA_BIND_REG`
  - `dma_bind_t`
- Logical interrupt support:
  - LD/LDG constants and register offsets.
  - `ldg_num_t`
  - `ldsv_t`
  - `ldsv2_t`
  - `ld_im_t`
  - `ldgimgm_t`
  - `ldgitmres_t`
  - `sid_t`
- Reset and error handling:
  - `rst_ctl_t`
  - `sys_err_mask_t`
  - `sys_err_stat_t`
- Meta arbiter and SMX/debug:
  - `dty_tid_ctl_t`
  - `dty_tid_stat_t`
  - `smx_cfg_dat_t`
  - `smx_int_stat_t`
  - `smx_ctl_t`
  - `smx_dbg_vec_t`
  - PIO debug/training/arbiter unions.
- GPIO and PIM register formats.
- Logical page partitioning structures:
  - `log_page_vld_t`
  - `log_page_mask_t`
  - `log_page_value_t`
  - `log_page_relo_t`
  - `log_page_hdl_t`

## Dependencies And Relationships
This header requires host endianness and bit ordering macros to be defined. It is included by `nxge_impl.h` and provides the global hardware register definitions used by FZC, interrupt, partitioning, and error-handling code.

## Research Notes
Most register formats are 64-bit unions with endian-specific 32-bit low-word layouts. `nxge_defs.h` also defines some overlapping interrupt constants; this header is the fuller hardware-register view.
