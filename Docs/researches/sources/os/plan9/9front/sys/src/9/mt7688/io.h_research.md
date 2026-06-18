# File Research: sources/os/plan9/9front/sys/src/9/mt7688/io.h

This header defines MT7688 memory-mapped I/O addresses and hardware register constants. `IO(t,x)` maps physical peripheral addresses through uncached `KSEG1`.

It covers system control, timers, memory counter, GPIO, I2C, I2S, SPI, UARTs, DMA, AES, Ethernet, switch, PCI, Wi-Fi, and USB base addresses. It also defines UART register offsets, system reset register offsets, CPU interrupt numbers, secondary SoC interrupt-controller interrupt IDs, interrupt-controller register offsets, timer/global timer bits, MCNT registers, PDMA Ethernet ring registers, switch DMA counters, and 10/100 switch register offsets.

This header is a hardware map shared by several MT7688 drivers in this group: `irq.c`, `i2c7688.c`, `uarti8250.c`, and likely Ethernet/USB/PCI code elsewhere. It is foundational rather than filesystem-specific, but block/network/filesystem availability on embedded systems depends on these low-level I/O definitions being correct.

Notable risks: comments mark some interrupt IDs as uncertain; `IRQshift` is defined with a trailing semicolon; the header encodes board/SoC assumptions directly.
