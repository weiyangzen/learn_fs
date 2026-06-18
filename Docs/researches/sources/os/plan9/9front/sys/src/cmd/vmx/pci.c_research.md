# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/pci.c

This file implements a simple PCI bus/config-space model.

Key behavior:
- Creates PCI devices, assigns incrementing BDFs, creates BARs and capabilities, and initializes a host bridge.
- Maintains linked lists of active memory and I/O BARs according to command register enable bits.
- Handles config address/data ports 0xcf8/0xcfc, including partial-byte masks.
- Exposes standard config fields: vendor/device, command/status, class/rev, BARs, subsystem ID, capability pointer, and interrupt line/pin.
- Tracks PCI IRQ activity and maps active device IRQs to PIC lines.
- `pcibusmap` auto-assigns I/O BAR addresses, rotates through a small IRQ set, sets ELCR level mode, and initially deasserts assigned IRQ lines.

Integration and risks:
- Memory BARs are mostly unsupported for bus mapping except for explicit users such as VGA.
- BAR sizing/rounding is minimal but adequate for vmx’s own virtio/VGA devices.
