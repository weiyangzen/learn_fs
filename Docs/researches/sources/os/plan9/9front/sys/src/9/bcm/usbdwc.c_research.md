# File Research: sources/os/plan9/9front/sys/src/9/bcm/usbdwc.c

USB host driver for the BCM2835 Synopsys DesignWare USB 2.0 OTG controller.

Key responsibilities:
- Registers HCI type `dwcotg`.
- Initializes controller FIFOs, DMA mode, host mode, power, and global interrupts.
- Allocates/releases host channels and configures endpoint channel state.
- Implements control, bulk, and interrupt endpoint read/write paths.
- Handles split transactions, SOF scheduling, NAK/NYET retries, stalls, channel halt, and DMA cache maintenance.
- Provides root-port enable, reset, power, and status methods.
- Uses FIQ-level interrupt handling for host-channel events and a timer IRQ to wake sleepers safely.

Important behavior:
- Isochronous pipes and bandwidth budgeting are explicitly unsupported.
- `Slowbulkin` works around a known bulk-IN DMA/channel lockup by reading packets individually.
- Control reads cache data in an endpoint-owned block until consumed by `ctldata()`.
- Endpoint open rejects unsupported transfer types.

Dependencies:
- `dwcotg.h`, Plan 9 USB core, DMA address/cache helpers, interrupt/timer infrastructure, VideoCore power control, and block allocator.
