# File Research: sources/os/plan9/9front/sys/src/9/zynq/io.h

Purpose: Zynq platform MMIO base-address and IRQ-number definitions.

Key interfaces:
- Base addresses for UART, USB, Ethernet, QSPI, SDIO, SLCR, DEVC, MPCORE, L2, OCM.
- IRQ numbers for timer, XADC, device config, USB, Ethernet, SDIO, UART.
- Interrupt trigger constants `LEVEL`, `EDGE`.
- `PS_CLK` and `XADCINTERVAL`.

Integration notes: Included by most Zynq platform drivers and assembly startup.

Risk/attention points: These constants encode the board/platform memory map; wrong values break early boot or device access.
