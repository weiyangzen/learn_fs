# File Research: sources/os/plan9/plan9/sys/src/9/bcm/usbdwc.c

BCM2835 USB HCI driver for the Synopsys DesignWare USB 2.0 OTG controller.

Key behavior:
- Registers HCI type `"dwcotg"` for `devusb.c`.
- Initializes host mode, powers USB through VideoCore, enables DMA, sizes FIFOs, flushes FIFOs, powers port 0, and enables host-channel interrupts.
- Manages host-channel allocation/release with a bitmap and `QLock`.
- Programs channel characteristics for device address, endpoint number/type, speed, max packet, and split transactions through hubs.
- Uses FIQ (`IRQusb`) for host-channel and SOF events; uses ARM timer IRQ as a deferred wakeup bridge for sleeping processes.
- Implements split-transaction retry/complete-split handling for full/low-speed devices behind hubs.
- `chanio()` programs DMA-backed transfers, waits for channel halt/interrupts, handles NAK/NYET/stall/error cases, updates transfer sizes, and logs debug channel state.
- `ctltrans()` implements USB control transfer setup/data/status phases and buffers IN control data for later reads.
- `epread()`/`epwrite()` implement control, bulk, and interrupt endpoint I/O with cache-aligned bounce buffers.
- Implements root-port enable, reset, and status synthesis for root hub emulation.

Limitations are noted in source comments: no isochronous pipes, no bandwidth budgeting, crude frame scheduling, optimistic error handling.
