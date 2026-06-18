# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_defs.h

## Purpose
Defines shared Neptune/NXGE hardware constants: block base addresses, DMA CSR offsets, ring sizing defaults, DMA channel limits, port/MAC/VLAN/TCAM/FCRAM limits, interrupt logical-device numbering, validation macros, and common register bitfield helper macros.

## Main Interfaces
- Block address constants for `PIO`, `FZC_PIO`, `FZC_MAC`, `FZC_IPP`, `FFLP`, `FZC_FFLP`, `PIO_VADDR`, `DMC`, `FZC_DMC`, `TXC`, `FZC_TXC`, interrupt-mask blocks, PROM, and PIM.
- DMC/TX register offsets such as `TX_RNG_CFIG`, `TX_RING_HDH`, `TX_RING_KICK`, `TX_CS`, `RDC_TBL`, logical page registers, RED registers, and DRR weight registers.
- Ring defaults for RBR/RCR/TDC and transmit gather pointers.
- Hardware limits: `NXGE_MAX_RDCS`, `NXGE_MAX_TDCS`, `NXGE_MAX_PORTS`, `NXGE_MAX_VRS`, `NXGE_MAX_RDC_GROUPS`, `NXGE_MAX_VLANS`, TCAM and hash sizes.
- Classification constants for TCAM formats, flow-key fields, and FCRAM match types.
- Address/bit helpers: `NXGE_BASE()`, `NXGE_VAL()`, `TDMC_PIOVADDR_OFFSET()`, `RDMC_PIOVADDR_OFFSET()`, `DMC_OFFSET()`, `TDMC_OFFSET()`.
- Validation macros for ports, TXDMA pages/functions/channels, VR pages, logical devices, timers, and SID vectors.

## Dependencies And Relationships
This is a foundational include used by nearly every NXGE per-block hardware header. It supplies base offsets consumed by `nxge_hw.h`, `nxge_mac_hw.h`, `nxge_ipp_hw.h`, `nxge_fflp_hw.h`, `nxge_espc_hw.h`, and driver implementation code.

## Research Notes
This header mixes active definitions with legacy/conditional blocks under `OLD` and `ORIGINAL`. It also contains a legacy-looking typo in the `LDGIMGN` macro reference, using `PIO_LDGIMGN` where the block base defined earlier is `PIO_LDGIM`.
