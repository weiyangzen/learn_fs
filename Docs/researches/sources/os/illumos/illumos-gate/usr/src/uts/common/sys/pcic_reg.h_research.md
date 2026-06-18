# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcic_reg.h

## Purpose
Defines Intel 82365SL-compatible PCIC/PCMCIA controller register offsets, bit masks, window layout constants, vendor-specific extension registers, interrupt masks, memory/I/O mapping encodings, and CardBus/Yenta socket registers.

## Main Interfaces
- Controller/socket topology:
  - `PCIC_MAX_CONTROLLERS`
  - `PCIC_SOCKETS`
  - `PCIC_MEMWINDOWS`
  - `PCIC_IOWINDOWS`
  - `PCIC_NUMWINDOWS`
  - `PCIC_NUMWINSOCK`
- Index/data register selection:
  - `PCIC_INDEX_REG0`
  - `PCIC_INDEX_REG1`
  - `PCIC_BASE0`
  - `PCIC_BASE1`
  - `PCIC_SOCKET_0`
  - `PCIC_SOCKET_1`
  - `PCIC_DATA_REG0`
  - `PCIC_DATA_REG1`
- Core socket registers:
  - `PCIC_CHIP_REVISION`
  - `PCIC_INTERFACE_STATUS`
  - `PCIC_POWER_CONTROL`
  - `PCIC_CARD_STATUS_CHANGE`
  - `PCIC_MAPPING_ENABLE`
  - `PCIC_INTERRUPT`
  - `PCIC_MANAGEMENT_INT`
  - I/O and memory window registers.
- Vendor-specific registers and bits for Cirrus Logic, Intel 82092AA, Vadem, Ricoh, O2 Micro, Texas Instruments, Toshiba, SMC, and Yenta/CardBus controllers.
- Card status, power, interrupt, change-detect, global-control, and misc-control masks.
- Memory/I/O mapping helpers:
  - `SYSMEM_LOW()`
  - `SYSMEM_HIGH()`
  - `SYSMEM_EXT()`
  - `SYSMEM_WINDOW()`
  - `CARDMEM_LOW()`
  - `CARDMEM_HIGH()`
  - `HIGH_BYTE()`
  - `LOW_BYTE()`
  - `IOMEM_WINDOW()`
  - `IOMEM_SETWIN()`
- Resource range constants:
  - `PCIC_PAGE`
  - `IOMEM_FIRST/LAST/MIN/MAX/GRAN/DECODE`
  - `MEM_FIRST/LAST/MIN/MAX`
  - `MEM_SPEED_MIN/MAX`
- CardBus registers and bit masks:
  - `CB_STATUS_EVENT`
  - `CB_STATUS_MASK`
  - `CB_PRESENT_STATE`
  - `CB_EVENT_FORCE`
  - `CB_CONTROL`
  - `CB_SOCKET_POWER`
  - `CB_*` status, event, power, and voltage bits.

## Dependencies And Relationships
Used by the PCIC driver implementation and paired with `pcic_var.h` soft-state definitions.

## Research Notes
The file covers both classic index/data PCIC register access and CardBus/Yenta memory-mapped socket registers, reflecting support for many legacy controller variants.
