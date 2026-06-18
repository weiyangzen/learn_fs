# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/si3124/si3124reg.h

## Role

Register, DMA descriptor, FIS, PRB, and error-code definition header for the Silicon Image 3124/3132/3531 SATA HBA driver.

## Key Elements

- Uses packed structures for hardware-facing layouts.
- `si_sge_t` describes one scatter/gather element with 64-bit address, byte count, and control bits for terminate/link.
- `si_sgt_t` groups four SGEs into one scatter/gather table.
- `fis_reg_h2d_t` models a SATA Register Host-to-Device FIS with macros to set and get command, features, LBA, sector count, device/head, and extended fields.
- `si_prb_t` models a Port Request Block with control override, received count, embedded H2D FIS, and initial SGEs.
- Defines interrupt bits for command completion, command error, port ready, power/PHY changes, unrecognized FIS, CRC/handshake errors, and device exchange.
- Defines disk/ATAPI/port-multiplier signatures.
- Defines global and per-port register address macros, including LRAM, port control/status, interrupt enable/status, command error, slot status, SCR registers, command activation, and signature offsets.
- Defines port-control/status bits, command posting macro `POST_PRB_ADDR`, slot masks, device IDs, BAR indexes, PSCR/SStatus fields, and command error codes.

## Dependencies and Coupling

The address macros assume `si_ctl_state_t` fields from `si3124var.h`. `POST_PRB_ADDR` also assumes per-port PRB/SGB DMA handles and the global `si_dma_sg_number`.

## Research Notes

This file is the hardware contract for command submission. The command activation path syncs both PRB and S/G memory for device access before writing the PRB physical address to the command-activation register.
