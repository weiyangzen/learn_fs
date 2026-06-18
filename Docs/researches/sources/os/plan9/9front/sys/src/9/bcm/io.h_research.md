# File Research: sources/os/plan9/9front/sys/src/9/bcm/io.h

BCM 32-bit platform interrupt and bus constants.

Key contents:
- Defines interrupt numbers for basic IRQs, GPU IRQs, DMA channels, USB, GPIO, I2C, SPI, UART, timers, mailbox, SD/MMC, and ARM-local interrupts.
- Provides `IRQDMA(chan)` for DMA interrupt numbering.
- Defines `BUSUNKNOWN` as `-1`.

Role:
- Shared by low-level BCM drivers to coordinate IRQ registration and device selection.

Dependencies:
- Consumed by interrupt controller, UART, USB, I2C, SD/MMC, and platform initialization code.
