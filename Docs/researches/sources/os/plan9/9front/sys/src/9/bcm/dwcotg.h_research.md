# File Research: sources/os/plan9/9front/sys/src/9/bcm/dwcotg.h

Register map and bit definitions for the Synopsys DesignWare USB 2.0 OTG host controller.

Key contents:
- Defines `Dwcregs` covering global, host, port, host-channel, FIFO, and power/clock registers.
- Defines host channel structure and `Maxchans`.
- Defines masks and symbolic values for OTG, AHB, USB config, reset, interrupts, RX status, FIFO sizing, hardware config, LPM, host config, port status, channel characteristics, split transactions, transfer sizing, and power gating.

Dependencies:
- Consumed by the BCM USB host driver.

Research notes:
- This header is declarative hardware interface data; it contains no executable functions.
