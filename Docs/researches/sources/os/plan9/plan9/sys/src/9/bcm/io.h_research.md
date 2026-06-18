# File Research: sources/os/plan9/plan9/sys/src/9/bcm/io.h

BCM interrupt, DMA, power, and clock numeric constants.

Key contents:
- IRQ numbers for system timers, USB, DMA channels, auxiliary UART, MMC, ARM basic timer, and FIQ source.
- `IRQDMA(chan)` macro.
- DMA direction constants: device-to-memory, memory-to-device, memory-to-memory.
- eMMC DMA channel/peripheral mapping constants.
- VideoCore power-domain IDs.
- VideoCore clock IDs.

These constants are consumed by timer, DMA, eMMC, UART, USB, VideoCore, and trap/interrupt code.
