# File Research: sources/os/plan9/plan9/sys/src/9/mtx/ether2114x.c

## Role

DEC/Intel 2114x Tulip-family Ethernet driver for the MTX port. It handles PCI discovery, descriptor rings, transmit/receive, interrupts, EEPROM/SROM parsing, MII management, media selection, and registration with the generic Ethernet layer.

This is network device driver code, not filesystem code.

## Main Interfaces

- `ether2114xlink()`: registers the driver.
- Hardware operations:
  - `reset`
  - `attach`
  - `transmit`
  - `interrupt`
  - `ifstat`
  - `promiscuous`
- Controller setup:
  - `dec2114xpci`
  - `ctlrinit`
  - `softreset`
  - `srom`
  - `media`
  - `mediaxx`

## Data Structures

- `Des`: RX/TX DMA descriptor.
- `Ctlr`: controller state with PCI info, rings, SROM data, media state, and statistics.
- Enums define CSR bits, descriptor status/control bits, PHY registers, media variants, and SROM block types.

## Important Behavior

- Uses descriptor rings for RX and TX DMA.
- Interrupt handler processes receive packets, transmit completion, abnormal conditions, link changes, and fatal bus errors.
- MII bit-banging is implemented via CSR9 helpers.
- SROM parser interprets type 0/2/5 blocks and PHY/symbol media blocks.
- Media selection handles fixed, MII, SYM, and SIA-style 2114x variants.
- PCI discovery matches supported vendor/device IDs and configures IO port, IRQ, and bus mastering.
- `reset` allocates rings, reads MAC address, installs callbacks, and initializes controller state.

## Dependencies And Assumptions

- Depends on `devether.c`/`etherif.h`.
- Uses PCI config helpers and I/O port accessors.
- Assumes cache coherency or explicit descriptor visibility appropriate for this platform.

## Notable Risks

- Very hardware-specific media/SROM parsing with many fallback paths.
- DMA descriptor ownership bits must be maintained exactly.
- Error handling resets or reinitializes hardware in interrupt context.
