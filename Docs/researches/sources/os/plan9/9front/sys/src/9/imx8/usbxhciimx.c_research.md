# File Research: sources/os/plan9/9front/sys/src/9/imx8/usbxhciimx.c

Role: i.MX8 USB xHCI host glue for clocks, PHY/core initialization, power domains, and Plan 9 xHCI registration.

Key responsibilities:
- Gates per-controller `usbN.ctrl` and `usbN.phy` clocks.
- Initializes USB PHY control registers: reset/ATE reset, reference SSP enable, TX enable, and clears resets.
- Initializes Synopsys DWC3 core registers for host mode, power-down scale, auto retry, and 30 MHz frame adjustment.
- `reset()` allocates up to two xHCI controllers at fixed MMIO bases, assigns IRQs, and links them to Plan 9 xHCI core.
- First-controller setup configures USB1 overcurrent/reset pads, toggles hub reset GPIO, disables both clocks, and programs shared USB bus/core/phy root rates.
- Powers up per-controller GPC domains `usb_otg1`/`usb_otg2`, gates clocks, initializes PHY and core.
- `usbxhciimxlink()` registers the `xhci` HCI type.

Dependencies:
- Plan 9 USB/xHCI core, GPC, CCM, GPIO, IOMUX, GIC.

Notes:
- Controller allocation is sequential; each `reset()` call claims the first nil slot.
- USB1 hub reset uses board-specific `gpio1_io14`.
