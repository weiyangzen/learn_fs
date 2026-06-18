# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_ipp_hw.h

## Purpose
Defines IPP hardware registers, address calculations, configuration bits, interrupt status/mask bits, ECC control layout, FIFO pointer masks, counter masks, and reset timing.

## Main Interfaces
- Register offsets for IPP config, discard/checksum/ECC counters, interrupt status/mask, PFIFO/DFIFO read/write data, FIFO pointers, state machine, checksum status, FFLP checksum info, debug select, ECC syndrome, EOP-miss pointer, and ECC control.
- Port address helpers:
  - `IPP_REG_ADDR(port_num, reg)`
  - `IPP_PORT_ADDR(port_num)`
- Configuration bits:
  - `IPP_SOFT_RESET`
  - `IPP_IP_MAX_PKT_BYTES_*`
  - PIO write enables
  - checksum/drop/ECC/enable bits.
- Interrupt status bits for missed SOP/EOP, DFIFO ECC classes, ECC entry index, PFIFO parity/index, PFIFO over/underflow, checksum counter max, and discard counter max.
- `ipp_status_t`: endian-aware interrupt status union.
- `ipp_ecc_ctrl_t`: endian-aware ECC injection/correction control union.
- Interrupt-mask disable bits, DFIFO entry counts, pointer masks, and counter masks.

## Dependencies And Relationships
Includes `nxge_defs.h` for `FZC_IPP`. Higher-level IPP software state and prototypes are in `nxge_ipp.h`.

## Research Notes
The port-address macros encode the non-linear IPP port layout for ports 0 through 3. The bitfield unions require one of `_BIT_FIELDS_HTOL` or `_BIT_FIELDS_LTOH`.
