# File Research: sources/os/plan9/plan9/sys/src/9/pc/usbehcipc.c

Purpose: PC-specific EHCI host-controller discovery/reset glue for Plan 9 USB. It scans PCI for EHCI controllers, maps registers, claims legacy BIOS ownership, resets/configures the controller, initializes generic EHCI memory/linkage, and registers the `ehci` HCI type.

Main logic:
- `scanpci` finds PCI USB controllers with programming interface `0x20`, maps BAR0, validates IRQ, allocates `Ctlr`, records capability and operational register pointers, enables PCI bus mastering and power state, and stores controllers in `ctlrs`.
- `getehci` walks the EHCI extended capability list to find legacy support, requests OS ownership from BIOS, waits for BIOS semaphore clear, disables SMIs, and clears config routing.
- `ehcireset` stops the controller, disables legacy mode, reclaims from BIOS, clears 64-bit segment register if needed, resets the controller unless it is the debug controller, sets interrupt threshold, and records frame-list size.
- `reset` honors `*maxehci` and `*nousbehci`, selects an inactive controller matching optional `hp->port`, fills `Hci` port/IRQ/TBDF/nports fields, calls `ehcireset`, `ehcimeminit`, and `ehcilinkage`, and installs shutdown/debug callbacks.
- `shutdown` resets/stops the controller and clears frame-list base.
- `usbehcilink` registers the HCI type name `ehci`.

Dependencies and integration:
- Uses Plan 9 USB HCI layer (`addhcitype`, `Hci`), generic EHCI code via `ehcilinkage`/`ehcimeminit`/`ehcirun`, PCI helpers, MMIO mapping, and power/bus-master setup.
- Includes `../port/usb.h`, `../port/portusbehci.h`, and local `usbehci.h`.

Risks and notes:
- `scanpci` is one-shot via `already`; controllers appearing later are not discovered.
- `maxehci` defaults to `Nhcis` but can limit active controllers; comments note some systems wedge with multiple EHCI controllers.
- Legacy BIOS handoff has a bounded wait and logs timeout but continues with SMI disabling/control clearing.
