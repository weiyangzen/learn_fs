# File Research: sources/os/plan9/plan9/sys/src/9/bcm/dwcotg.h

Register layout and bit definitions for the Synopsys DesignWare USB 2.0 OTG controller as used by BCM2835.

Key contents:
- Defines `Dwcregs` register map for global, host, port, host-channel, FIFO, and power/clock-gating registers.
- Defines `Hostchan` register layout inside `Dwcregs`.
- Enumerates global control/status bits (`gotgctl`, `gahbcfg`, `gusbcfg`, `grstctl`, `gintsts`, etc.).
- Enumerates FIFO sizing/status fields, hardware config fields, host config/frame fields, host port state bits, host channel characteristic/split/interrupt/transfer-size bits, PID encodings, and power/clock controls.
- Provides constants used heavily by `usbdwc.c` for reset, host mode, DMA, FIFO setup, channel setup, split transactions, interrupt handling, and port status synthesis.

No executable logic is present.
