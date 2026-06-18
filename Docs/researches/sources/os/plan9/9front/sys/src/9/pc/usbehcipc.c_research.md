# File Research: sources/os/plan9/9front/sys/src/9/pc/usbehcipc.c

## Role

PC-specific PCI discovery, reset, BIOS handoff, and HCI registration glue for the EHCI USB 2.0 driver.

## Main Interfaces

- `usbehcilink()` registers HCI type `ehci` with `addhcitype()`.
- `reset(Hci *hp)` claims an inactive EHCI controller and links it to the generic EHCI HCI implementation.
- Provides HCI `shutdown` and `debug` callbacks.

## Key Behavior

- `scanpci()` finds PCI USB EHCI controllers by class/subclass/programming-interface, maps MMIO BAR0, and builds a static controller list.
- `ehciecap()` walks EHCI extended PCI capabilities.
- `getehci()` performs BIOS-to-OS handoff through legacy support semaphores unless `*noehcihandoff` is set, then disables EHCI SMIs.
- `ehcireset()` disables interrupts, stops the controller, routes ports away while setting up, resets the host controller, clears high address segment when 64-bit capable, and records frame-list size.
- `reset()` honors `*nousbehci`, enables PCI, fills `Hci` port/IRQ/TBDF/port count, initializes EHCI memory, enables bus mastering, installs generic EHCI linkage, and registers interrupts.
- `shutdown()` disables interrupts, resets the controller, stops it, and clears frame-list base.

## Dependencies And Assumptions

- Depends on `../port/usb.h`, `usbehci.h`, PCI enumeration, MMIO mapping, and generic EHCI functions from other files.
- Assumes BAR0 is MMIO and skips I/O BAR controllers.
- Uses only one active claim per scanned controller.

## Research Notes

- This file is platform glue; transfer scheduling and endpoint mechanics live elsewhere.
- BIOS handoff and SMI disabling are the most important PC-specific safety steps before the generic EHCI driver starts running.
