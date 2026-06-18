# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_espc_hw.h

## Purpose
Defines low-level ESPC/EPC register offsets and bit masks for accessing the PROM/NCR region through NXGE PIO.

## Main Interfaces
- PIO enable/status registers:
  - `ESPC_PIO_EN_REG`
  - `ESPC_PIO_EN_MASK`
  - `ESPC_PIO_STATUS_REG`
- EPC status/control bits for read/write initiate and complete, EEPROM address and data fields, and wait timing.
- NCR addressing helpers:
  - `ESPC_NCR_REG`
  - `ESPC_REG_ADDR(reg)`
  - `ESPC_NCR_REGN(n)`
  - `ESPC_NCR_VAL_MASK`

## Dependencies And Relationships
Includes `nxge_defs.h` for the `FZC_PROM` block base. Higher-level SPROM field names are layered in `nxge_espc.h`.

## Research Notes
This is the hardware access companion to `nxge_espc.h`; it only defines offsets and masks needed to address the PROM/NCR data.
