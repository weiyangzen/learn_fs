# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcic_var.h

## Purpose
Defines PCIC driver-private soft state for controllers, sockets, memory/I/O windows, debounce and simulated power management, controller flags, interrupt modes, bus resource layout constants, known chip IDs, and PCIC range-property layout.

## Main Interfaces
- PM simulation constants and state:
  - `PCIC_PM_TIME`
  - `PCIC_PM_DETWIN`
  - `PCIC_PM_METHOD_*`
  - `PCIC_PM_INIT`
  - `PCIC_PM_RUN`
  - `pcic_pm_t`
- Debounce/ready wait constants:
  - `PCIC_REM_DEBOUNCE_CNT`
  - `PCIC_REM_DEBOUNCE_TIME`
  - `PCIC_DEBOUNCE_OK_CNT`
  - `PCIC_READY_WAIT_LOOPS`
  - `PCIC_READY_WAIT_TIME`
- Window structures:
  - `pcs_memwin_t`
  - `pcs_iowin_t`
  - `PCW_MAPPED`, `PCW_ENABLED`, `PCW_ATTRIBUTE`, `PCW_WP`, `PCW_OFFSET`
- Socket state:
  - `pcic_socket_t`
  - `PCS_CARD_PRESENT`
  - `PCS_CARD_IDENTIFIED`
  - `PCS_CARD_ENABLED`
  - `PCS_IRQ_ENABLED`
  - `PCS_CARD_IO`
  - `PCS_CARD_16BIT`
  - `PCS_CARD_ISCARDBUS`
  - `PCS_DEBOUNCING`
  - related socket flags.
- Controller state:
  - `pcic_debounce_state_t`
  - `pcicdev_t`
- Controller flags:
  - `PCF_ATTACHED`
  - `PCF_CALLBACK`
  - `PCF_INTRENAB`
  - `PCF_USE_SMI`
  - `PCF_CBPWRCTL`
  - `PCF_PCIBUS`
  - `PCF_CARDBUS`
  - `PCF_DMA`
  - `PCF_ZV`
  - many variant flags for voltage, IRQ, I/O remap, debounce, and memory-page behavior.
- Interrupt modes and I/O access types:
  - `PCIC_INTR_MODE_ISA`
  - `PCIC_INTR_MODE_PCI`
  - `PCIC_INTR_MODE_PCI_1`
  - `PCIC_INTR_MODE_PCI_S`
  - `PCIC_IO_TYPE_82365SL`
  - `PCIC_IO_TYPE_YENTA`
- Bus resource layout constants for PCI and ISA register properties.
- Chip/vendor IDs and type strings for Intel, Cirrus Logic, Vadem, TI, O2 Micro, ENE, SMC, Ricoh, Toshiba, and generic Yenta devices.
- Card classification and timing helpers:
  - `PCIC_PCI_CLASS()`
  - `PCIC_PCI_PCMCIA`
  - `PCIC_PCI_CARDBUS`
  - `PCIC_MEM_AM`
  - `PCIC_MEM_CM`
  - `mhztons()`
- Event capability defaults:
  - `PCIC_DEFAULT_INT_CAPS`
  - `PCIC_DEFAULT_RPT_CAPS`
  - `PCIC_DEFAULT_CTL_CAPS`
- `pcic_ranges_t`: `ranges` property format.

## Dependencies And Relationships
Depends on `pcic_reg.h`, PCI constants, Card Services event masks, and DDI interrupt/mapping types through includers. It is private to the PCIC driver and controller-specific attach/interrupt paths.

## Research Notes
The soft state tracks both legacy ISA-style and PCI/Yenta-style controllers. Many flags exist to encode chip-specific errata and routing modes rather than abstract PCMCIA behavior.
